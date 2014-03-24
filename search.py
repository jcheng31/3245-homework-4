#!/env/bin/python
import os
import argparse


def main(args):
    args.dictionary = os.path.abspath(args.dictionary)
    args.postings = os.path.abspath(args.postings)
    args.queries = os.path.abspath(args.queries)
    args.output = os.path.abspath(args.output)

    # TODO:

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='boolean retrieval \
                                     assignment.')
    parser.add_argument('-d', '--dictionary', type=str,
                        help='dictionary file.', default='dictionary.txt')
    parser.add_argument('-p', '--postings', type=str, help='postings file.',
                        default='postings.txt')
    parser.add_argument('-q', '--queries', type=str, help='queries file.',
                        required=True)
    parser.add_argument('-o', '--output', type=str, help='output file.',
                        default='results.txt')
    args = parser.parse_args()
    main(args)
