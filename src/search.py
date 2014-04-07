#!/env/bin/python
import argparse
import collections
import compoundindex
import os
import patentfields
import utils

from features import vsm, fields
from helpers import cache
from parser import free_text as tokenizer
from queryexpansion import expand, synonym_expansion


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

    # Declaration of features and their weights.
    FEATURES = [
        (vsm.VSMTitle(),                                4),
        (vsm.VSMAbstract(),                             2),
        (vsm.VSMTitleAndAbstract(),                     1),

        (vsm.VSMTitleMinusStopwords(),                  0),
        (vsm.VSMAbstractMinusStopwords(),               0),
        (vsm.VSMTitleAndAbstractMinusStopwords(),       0),

        # fields only serve to boost scores of documents that are relevant.
        (fields.CitationCount(),                        0.5),
    ]

    # Declaration of query expanders to use.
    EXPANSION_PROCS = [
        synonym_expansion
    ]

    def __init__(self, query_xml, compound_index):
        self.__compound_index = compound_index
        self.__query = utils.parse_query_xml(query_xml)

        self.__tokens = {
            patentfields.TITLE: tokenizer(self.query_title),
            patentfields.ABSTRACT: tokenizer(self.query_description),
        }

        self.features, self.features_weights = zip(*self.FEATURES)
        self.features_vector_key = [f.NAME for f in self.features]

    def override_features_weights(self, weights):
        """Overrides specified feature weights.

        Used for learning/trainig the coefficients to fit the training data.
        """
        # new weights need to have the same cardinality since we do a
        # dot-product at the end
        assert len(weights) == len(self.features_weights)
        self.old_features_weights = self.features_weights
        self.features_weights = weights

    @cache.naive_class_method_cache
    def get_tokens_for(self, index, expand_query=False):
        tokens = self.__tokens.get(index)
        if not expand_query:
            return tokens

        # Expand query
        return expand(tokens, *self.EXPANSION_PROCS)

    def execute(self, verbose=False):
        """Returns a list of document names that satisfy the query.

        Documents are returned in order of relevance. If the verbose argument
        is set, returns a list of lists, where each list item is of format:

            [<score>, <feature vector scores>, doc_id]
            ...
        """
        shared_obj = SharedSearchObject()

        for feature in self.features:
            try:
                feature(self, shared_obj)
            except Exception, e:
                # NOTE(michael): This is for the competition framework. (When
                # an error occurs during search, there is no log/entry at all.
                import traceback
                tb = traceback.format_exc()
                print "# Error in feature: %s\n%s" % (feature.NAME, tb)

        results = self.calculate_score(shared_obj.doc_ids_to_scores)
        results.sort(reverse=True)  # Highest score first.

        if verbose:
            retval = []
            for elem in results:
                elem = list(elem)
                elem[-1] = self.compound_index.\
                    document_name_for_guid(str(elem[-1]))
                retval.append(elem)
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
            doc_score = utils.dot_product(doc_score_vector,
                                          self.features_weights)
            results.append((doc_score, doc_score_vector, doc_id))
        return results

    query_title = property(lambda self: self.__query['title'])
    query_description = property(lambda self: self.__query['description'])
    compound_index = property(lambda self: self.__compound_index)


class SharedSearchObject(object):
    """Simple case class, used as a shared object between search features.

    Used to pass, reuse values (if required by features that share common
    logic.)
    """
    def __init__(self):
        self.doc_ids_to_scores = {}

    def has_score(self, doc_id):
        return self.doc_ids_to_scores.get(doc_id)

    def set_feature_score(self, feature, doc_id, score):
        if not self.doc_ids_to_scores.get(doc_id):
            self.doc_ids_to_scores[doc_id] = {}
        self.doc_ids_to_scores[doc_id][feature] = score


def main(args):
    dictionary_file = os.path.abspath(args.dictionary)
    postings_file = os.path.abspath(args.postings)
    query_file = os.path.abspath(args.query)
    output_file = os.path.abspath(args.output)

    # NOTE(michael): Do these things outside the search class to allow
    # dependency injection at runtime/testing.
    compound_index = compoundindex.CompoundIndex(dictionary_file)
    with open(query_file, 'r') as f:
        query_xml = f.read()

    s = Search(query_xml, compound_index)
    results = s.execute()

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
