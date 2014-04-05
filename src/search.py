#!/env/bin/python
import os
import argparse
import collections
import utils
import compoundindex
import textprocessors

from features import boolean


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
        (boolean.Boolean(), 1),
    ]

    def __init__(self, dictionary_file, postings_file, query_file, output_file):
        self.dictionary_file = dictionary_file
        self.postings_file = postings_file
        self.query_file = query_file
        self.output_file = output_file
        self.__compound_index = compoundindex.CompoundIndex(dictionary_file)
        self.__query = utils.parse_query_file(query_file)

    query_title = property(lambda self: self.__query['title'])
    query_description = property(lambda self: self.__query['description'])
    compound_index = property(lambda self: self.__compound_index)

    @property
    def query_title_tokens(self):
        return textprocessors.generic_tokenizer(self.query_title)

    @property
    def query_description_tokens(self):
        return textprocessors.generic_tokenizer(self.query_description)

    @property
    def query_tokens(self):
        tokens = self.query_title_tokens
        tokens.extend(self.query_description_tokens)
        return tokens

    def execute(self):
        shared_obj = SharedSearchObject()

        for feature, _ in self.FEATURE_WEIGHT_TUPLE:
            feature(self, shared_obj)

        return shared_obj.doc_ids_to_scores


class SharedSearchObject(object):
    """Simple case class, used as a shared object between search features.

    Used to pass, reuse values (if required by features that share common
    logic.)
    """
    def __init__(self):
        self.doc_ids_to_scores = collections.defaultdict(dict)

    def set_layer_score(self, doc_id, layer, score):
        self.doc_ids_to_scores[doc_id][layer] = score


def main(args):
    dictionary_file = os.path.abspath(args.dictionary)
    postings_file = os.path.abspath(args.postings)
    query_file = os.path.abspath(args.query)
    output_file = os.path.abspath(args.output)

    s = Search(dictionary_file, postings_file, query_file, output_file)
    print s.execute()


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
