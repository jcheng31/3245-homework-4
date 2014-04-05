#!/env/bin/python
import argparse
import collections
import compoundindex
import os
import patentfields
import utils

from features import vsm
from textprocessors import generic_tokenizer as tokenizer


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
    predefined thresholds to arrive at a final absolute score for each document.

    Notice that the thresholds of particular features can therefore be tweaked
    independent of other to tune the search system based on feedback.
    """

    # Declaration of features and their weights.
    FEATURE_WEIGHT_TUPLE = [
        (vsm.VectorSpaceModelTitle(),               4),
        (vsm.VectorSpaceModelAbstract(),            2),
        (vsm.VectorSpaceModelTitleAndAbstract(),    1),
    ]

    def __init__(self, dictionary_file, postings_file, query_file):
        self.dictionary_file = dictionary_file
        self.postings_file = postings_file
        self.query_file = query_file
        self.__compound_index = compoundindex.CompoundIndex(dictionary_file)
        self.__query = utils.parse_query_file(query_file)
        self.__tokens = {
            patentfields.TITLE: tokenizer(self.query_title),
            patentfields.ABSTRACT: tokenizer(self.query_description),
        }
        self.features, self.features_weights = zip(*self.FEATURE_WEIGHT_TUPLE)
        self.features_vector_key = [f.NAME for f in self.features]

    def get_tokens_for(self, index):
        return self.__tokens.get(index)

    def execute(self):
        shared_obj = SharedSearchObject()

        for feature in self.features:
            feature(self, shared_obj)

        results = self.calculate_score(shared_obj.doc_ids_to_scores)
        results.sort(reverse=True) # Highest score first.
        return [doc_id for score, doc_id in results]

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
            results.append((doc_score, doc_id))
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
        self.doc_ids_to_scores = collections.defaultdict(dict)

    def set_feature_score(self, feature, doc_id, score):
        self.doc_ids_to_scores[doc_id][feature] = score


def main(args):
    dictionary_file = os.path.abspath(args.dictionary)
    postings_file = os.path.abspath(args.postings)
    query_file = os.path.abspath(args.query)
    output_file = os.path.abspath(args.output)

    s = Search(dictionary_file, postings_file, query_file)
    results = s.execute()

    # Write results to file.
    with open(output_file, 'w+') as output:
        results = [str(x) for x in results]
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
