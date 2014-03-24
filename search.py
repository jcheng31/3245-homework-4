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
    parser = argparse.ArgumentParser(description='Patsnap assignment.')
    parser.add_argument('-d', '--dictionary', type=str,
                        help='dictionary file.', default='dictionary.txt')
    parser.add_argument('-p', '--postings', type=str, help='postings file.',
                        default='postings.txt')
    parser.add_argument('-q', '--query', type=str, help='query file.',
                        required=True)
    parser.add_argument('-o', '--output', type=str, help='output file.',
                        default='results.txt')
    args = parser.parse_args()
    main(args)
