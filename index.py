#!/env/bin/python
import os
import argparse


def main(args):
    args.index = os.path.abspath(args.index)
    args.dictionary = os.path.abspath(args.dictionary)
    args.postings = os.path.abspath(args.postings)

    indexer = Indexer(args.index, args.dictionary, args.postings)
    indexer.process_index()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='boolean retrieval ' +
                                     'assignment.')
    parser.add_argument('-i', '--index', type=str, help='directory of ' +
                        'of documents.', required=True)
    parser.add_argument('-d', '--dictionary', type=str, help='dictionary ' +
                        'file.', default='dictionary.txt')
    parser.add_argument('-p', '--postings', type=str, help='postings file.',
                        default='postings.txt')
    args = parser.parse_args()
    main(args)
