#!/env/bin/python
import os
import argparse
import utils
import compoundindex


class Search(object):
    def __init__(self, dictionary_file, postings_file, query_file, output_file):
        self.dictionary_file = dictionary_file
        self.postings_file = postings_file
        self.query_file = query_file
        self.output_file = output_file

        self.compound_index = compoundindex.CompoundIndex(dictionary_file)
        self.query = utils.parse_query_file(query_file)

    def execute(self):
        # TODO(michael)
        pass


def main(args):
    dictionary_file = os.path.abspath(args.dictionary)
    postings_file = os.path.abspath(args.postings)
    query_file = os.path.abspath(args.query)
    output_file = os.path.abspath(args.output)

    s = Search(dictionary_file, postings_file, query_file, output_file)
    s.execute()


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
