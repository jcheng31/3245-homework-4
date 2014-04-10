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
    feature).

    For instance, a basic implementation could have two features:

        - boolean query
        - number of citations

    After passing the query through the two features, each document will have a
    tuple representing its score. (If a score is not set, we default the score
    to 0).

        eg.
            (a1, a2)
            (b1, b2)
            (c1, c2)
            ...

    We then do a dot product of these scores against a tuple of various
    predefined thresholds to arrive at a final absolute score for each
    document.

    Notice that the thresholds of particular features can therefore be tweaked
    independent of other to tune the search system based on feedback.
    """

    # Arbitrary minimum score of a relevant document.
    MIN_SCORE = 1

    # Declaration of features and their weights.
    FEATURES = [
        (vsm.VSMTitle(),                                0),
        (vsm.VSMAbstract(),                             0),
        (vsm.VSMTitleAndAbstract(),                     0),

        (vsm.VSMTitleMinusStopwords(),                  10),
        (vsm.VSMAbstractMinusStopwords(),               8),
        (vsm.VSMTitleAndAbstractMinusStopwords(),       6),

        (vsm.VSMTitleMinusStopwordsPlusExpansion(),     5),
        (vsm.VSMAbstractMinusStopwordsPlusExpansion(),  5),

        # (ipc.IPCSectionLabelsTitle(),                   1),
        # (ipc.IPCSectionLabelsAbstract(),                1),

        # clusters
        (cluster.cluster_feature_generator(
            patentfields.IPC_SECTION)(),                1),
        (cluster.cluster_feature_generator(
            patentfields.IPC_CLASS)(),                  2),
        (cluster.cluster_feature_generator(
            patentfields.IPC_GROUP)(),                  4),
        (cluster.cluster_feature_generator(
            patentfields.IPC_PRIMARY)(),                6),
        (cluster.cluster_feature_generator(
            patentfields.IPC_SUBCLASS)(),               8),
        (cluster.cluster_feature_generator(
            patentfields.ALL_IPC)(),                    10),

        (cluster.cluster_feature_generator(
            patentfields.ALL_UPC)(),                    1),
        (cluster.cluster_feature_generator(
            patentfields.UPC_PRIMARY)(),                1),
        (cluster.cluster_feature_generator(
            patentfields.UPC_CLASS)(),                  1),

        (fields.CitationCount(),                        1),

        (relation.Citations(),                          0),
        (relation.FamilyMembers(),                      0),
    ]

    def __init__(self, query_xml, compound_index):
        self.__compound_index = compound_index
        self.__query = utils.parse_query_xml(query_xml)

        # Dictionary containing the raw text for the query's title and description.
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
        """Executes the search by running all features."""
        # Loop through all our feature functions. Each feature
        # updates self.shared_search_obj with its score for
        # each document.
        for feature in self.features:
            try:
                feature(self, self.shared_search_obj)
            except Exception, e:
                import traceback
                tb = traceback.format_exc()
                print "# Error in feature: %s\n%s" % (feature.NAME, tb)

        return self

    def results(self, verbose=False):
        """Returns a list of documents that match the search query, in order
        of relevance.

        If the verbose argument is set, returns a dictionary keyed by document
        name and with value:

            [<score>, <feature vector scores>, doc_id]
            ...

        NOTE: This is separated from execute so we can vary weights during the
        learning phase without recomputing the unweighted feature scores.
        """

        # Generate a list of documents, in descending order of relevance,
        # where the score of each document is above our threshold.
        results = self.calculate_score(
            self.shared_search_obj.doc_ids_to_scores)
        results.sort(reverse=True)  # Highest score first.
        results = [r for r in results if r[0] > self.min_score]

        if verbose:
            # Instead, generate the dictionary described in the docstring
            # above and return it.
            retval = {}
            for elem in results:
                doc_name = self.compound_index.document_name_for_guid(
                    str(elem[-1]))
                retval[doc_name] = elem
            return retval

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
        # Remove description prefix
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

    def has_score(self, doc_id):
        """Given a document ID, returns whether or not
        that document already has some score recorded."""
        return self.doc_ids_to_scores.get(doc_id)

    def set_feature_score(self, feature, doc_id, score):
        """Given a feature name, document ID, and a score,
        updates the score of that document ID for the feature."""
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

    # NOTE(michael): Lazy to format the weights nicely above...
    s.override_features_weights([
        -4.76077042,
        -10.78278743,
        7.68774728,
        0.94963462,
        -8.45635778,
        0.82181193,
        1.01882405,
        1.00527037,
        3.58792896,
        7.76432611,
        3.1524329,
        0.9973575,
        1.,
        3.58792896,
        1.01279276,
        -0.16678862,
        0.32148819,
        2.73311628,
        0,
        0,
    ])

    results = s.results()

    # Write results to file.
    with open(output_file, 'w+') as output:
        output.write('%s\n' % ' '.join(results))


if __name__ == '__main__':
    print 'version: 1'

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
