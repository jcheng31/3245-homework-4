#!/env/bin/python
import os
import argparse
import utils
import compoundindex
import textprocessors

from layers import booleanlayer


class Search(object):
    LAYERS = [
        booleanlayer.BooleanLayer(),
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
        # Start with a clean slate.
        candidate_doc_ids = []

        for layer in self.LAYERS:
            candidate_doc_ids = layer(self, candidate_doc_ids)

        return candidate_doc_ids


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
