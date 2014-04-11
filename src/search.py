#!/env/bin/python
import argparse
import collections
import compoundindex
import json
import os
import patentfields
import utils
import string

from features import vsm, fields, ipc, cluster, relation
from helpers import cache
from tokenizer import free_text as tokenizer


class Search(object):
    """Main search object.

    The main method is `execute`, which basically performs the search query by
    passing it through the various features (to calculate the score for the
    feature). The results of the search can be retrieved using the `results`
    method.

    At a high level, the search calculate the feature scores for each document
    and aggregates these scores into a feature score vector.

        doc1 => (s1, s2, ... sn),
        doc2 => (s1, s2, ... sn),
        ...

    Each of these features could be a simple vsm on a single index, or a score
    based on how many citations the document has.

    We then do a dot product of these scores against a tuple of various
    predefined thresholds to arrive at a final absolute score for each
    document.

    Based on these scores, the documents are sorted and returned in order.
    (We optionally have a min score that defines a minimum score that a
    document has to hit in order to qualify as 'relevant')

    Notice that the weights of particular features can therefore be tweaked
    independently of other features to tune the search system based on
    feedback/training.
    """

    # Arbitrary minimum score of a relevant document.
    MIN_SCORE = 1

    # Declaration of features and their weights.
    FEATURES = [
        (vsm.single.VSMTitle(),                                 -5.31243308),
        (vsm.single.VSMAbstract(),                              -9.30356609),
        (vsm.single.VSMTitleMinusStopwords(),                   1.27085722),
        (vsm.single.VSMAbstractMinusStopwords(),                -8.83578166),
        (vsm.single.VSMTitleNounsOnly(),                        0.000146222472),
        (vsm.single.VSMAbstractNounsOnly(),                     0.0000824446915),

        (vsm.multiple.VSMTitleAndAbstract(),                    5.59690266),
        (vsm.multiple.VSMTitleAndAbstractMinusStopwords(),      0.572786546),

        (vsm.expansion.VSMTitleMinusStopwordsPlusExpansion(),   1.10834491),
        (vsm.expansion.VSMAbstractMinusStopwordsPlusExpansion(),1.13443603),

        # clusters
        (cluster.cluster_feature_generator(
            patentfields.IPC_SECTION)(),                        4.48495518),
        (cluster.cluster_feature_generator(
            patentfields.IPC_CLASS)(),                          -0.00504756358),
        (cluster.cluster_feature_generator(
            patentfields.IPC_GROUP)(),                          1.64642283),
        (cluster.cluster_feature_generator(
            patentfields.IPC_PRIMARY)(),                        0.769168418),
        (cluster.cluster_feature_generator(
            patentfields.IPC_SUBCLASS)(),                       0.929689840),
        (cluster.cluster_feature_generator(
            patentfields.ALL_IPC)(),                            16.5908845),

        (cluster.cluster_feature_generator(
            patentfields.ALL_UPC)(),                            1.03998143),
        (cluster.cluster_feature_generator(
            patentfields.UPC_PRIMARY)(),                        -0.266005728),
        (cluster.cluster_feature_generator(
            patentfields.UPC_CLASS)(),                          -0.599552688),

        (fields.CitationCount(),                                3.05807617),

        # Unused features (these don't seem to work too well. Oh well.)
        # (relation.Citations(),                                  0),
        # (relation.FamilyMembers(),                              0),
        # (ipc.IPCSectionLabelsTitle(),                           1),
        # (ipc.IPCSectionLabelsAbstract(),                        1),
    ]

    def __init__(self, query_xml, compound_index):
        self.__compound_index = compound_index
        self.__query = utils.parse_query_xml(query_xml)

        # Dictionary containing the raw text for the query's title and
        # description.
        self.__text = {
            patentfields.TITLE: self.query_title,
            patentfields.ABSTRACT: self.query_description
        }

        self.min_score = self.MIN_SCORE
        # Set up lists to represent the feature functions and
        # their associated weights.
        self.features = []
        self.features_weights = []
        self.features_vector_key = []
        for f, weight in self.FEATURES:
            self.features.append(f)
            self.features_weights.append(weight)
            self.features_vector_key.append(f.NAME)

        # Set up our "global" object to share information
        # between feature functions.
        self.shared_search_obj = SharedSearchObject()

    def override_features_weights(self, weights):
        """Overrides specified feature weights.

        Used for learning/trainig the coefficients to fit the training data.
        """
        # new weights need to have the same cardinality since we do a
        # dot-product at the end
        assert len(weights) == len(self.features_weights)
        self.features_weights = weights

    def override_min_score(self, min_score):
        """Overrides the min_score."""
        self.min_score = min_score

    def get_tokens_for(self, index, unstemmed=False):
        """Given an index (title or abstract), returns a list of tokens
        from the words contained in that index.

        By default, this will return case-folded and stemmed tokens. If
        the unstemmed argument is set to True, the original words will be
        returned instead."""
        raw_text = self.__text.get(index)

        if unstemmed:
            # We need to return just the words, without any punctuation.
            words = raw_text.split()
            stripped = [x.strip(string.punctuation) for x in words]
            return stripped

        tokens = tokenizer(raw_text)

        # We want to strip out tokens which consist of just
        # punctuation characters.
        return [x for x in tokens if x not in string.punctuation]

    def execute(self):
        """Executes the search by iterating through all features.

        Since features can be added arbitrarily and are typically added by
        multiple developers, we add a try catch here for each feature. Failure
        of one feature should not take down the entire system."""
        # Loop through all our feature functions. Each feature updates
        # self.shared_search_obj with its score for each document.
        for feature in self.features:
            try:
                feature(self, self.shared_search_obj)
            except Exception, e:
                import traceback
                tb = traceback.format_exc()
                print "# Error in feature: %s\n%s" % (feature.NAME, tb)

        return self

    def results(self):
        """Returns a list of documents that match the search query, in order
        of relevance.

        NOTE: This is separated from execute so we can vary weights during the
        learning phase without recomputing the unweighted feature scores.
        """
        # Generate a list of documents, in descending order of relevance,
        # where the score of each document is above our threshold.
        results = self.calculate_score(
            self.shared_search_obj.doc_ids_to_scores)

        # Highest score first.
        results.sort(reverse=True)

        # Filter out results below the min_score
        results = [r for r in results if r[0] > self.min_score]

        return [self.compound_index.document_name_for_guid(str(elem[-1]))
                for elem in results]

    def calculate_score(self, doc_ids_to_scores):
        """Returns a list of (score, doc_id).

        Calculates the dot product between each document's score for each
        feature and the respective feature weights."""
        results = []
        for doc_id, score in doc_ids_to_scores.iteritems():
            doc_score_vector = [score.get(key, 0) for key in
                                self.features_vector_key]

            doc_score = utils.dot_product(
                doc_score_vector, self.features_weights)

            results.append((doc_score, doc_score_vector, doc_id))
        return results

    query_title = property(lambda self: self.__query['title'])
    compound_index = property(lambda self: self.__compound_index)

    @property
    def query_description(self):
        """Returns the description of the query, less the standard prefix."""
        description_prefix = 'Relevant documents will describe '
        raw = self.__query['description']
        if raw.startswith(description_prefix):
            raw = raw[len(description_prefix):]
        return raw


class SharedSearchObject(object):
    """Simple case class, used as a shared object between search features.

    Used to pass, reuse values (if required by features that share common
    logic.)
    """
    def __init__(self):
        self.doc_ids_to_scores = {}

    def set_feature_score(self, feature, doc_id, score):
        """Given a feature name, document ID, and a score, updates the score of
        that document ID for the feature."""
        if not self.doc_ids_to_scores.get(doc_id):
            self.doc_ids_to_scores[doc_id] = {}
        self.doc_ids_to_scores[doc_id][feature] = score


def main(args):
    dictionary_file = os.path.abspath(args.dictionary)
    postings_file = os.path.abspath(args.postings)
    query_file = os.path.abspath(args.query)
    output_file = os.path.abspath(args.output)

    # Open the dictionary.
    # NOTE(michael): Do these things outside the search class to allow
    # dependency injection at runtime/testing.
    with open(dictionary_file, 'r') as f:
        json_obj = json.load(f)

    compound_index = compoundindex.CompoundIndex(json_obj)

    # Load the query file.
    with open(query_file, 'r') as f:
        query_xml = f.read()

    # Execute the query.
    s = Search(query_xml, compound_index)
    s.execute()
    results = s.results()

    # Write results to file.
    with open(output_file, 'w+') as output:
        output.write('%s\n' % ' '.join(results))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Patsnap assignment - Search')
    parser.add_argument('-d', '--dictionary', required=True,
                        help='dictionary file.')
    parser.add_argument('-p', '--postings', required=True,
                        help='postings file.')
    parser.add_argument('-q', '--query', required=True,
                        help='query file.')
    parser.add_argument('-o', '--output', required=True,
                        help='output file.')
    args = parser.parse_args()
    main(args)
