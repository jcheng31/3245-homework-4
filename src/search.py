#!/env/bin/python
import os
import argparse
import search_patents


def main(args):
    args.dictionary = os.path.abspath(args.dictionary)
    args.postings = os.path.abspath(args.postings)
    args.query = os.path.abspath(args.query)
    args.output = os.path.abspath(args.output)
    search_patents.search(args.dictionary, args.postings, args.query,
                          args.output)


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
