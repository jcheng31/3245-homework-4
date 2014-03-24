#!/env/bin/python
import os
import argparse


class Query(object):
    def __init__(self, index):
        pass

    def run(self):
        return []


def run_queries(index, queries):
    """
    Runs each query against the index.
    """
    queries = read_queries(queries)
    results = []
    for q in queries:
        query = Query(q, index)
        documents = query.run()
        results.append(documents)
    return results


def read_queries(query_path):
    """
    Reads a list of queries from the input query file.

    We assume that each query is on a separate line. Blank lines are ignored.
    """
    queries = list()
    with open(query_path, 'r') as f:
        for line in f:
            queries.append(line.strip())
    return [q for q in queries if q]


def write_results(results, path):
    """
    Writes python lists of results to the output file in the requisite
    format.
    """
    with open(path, 'w') as f:
        f.write('\n'.join([' '.join([str(r) for r in result_list])
                           for result_list in results]))


def main(args):
    args.dictionary = os.path.abspath(args.dictionary)
    args.postings = os.path.abspath(args.postings)
    args.queries = os.path.abspath(args.queries)
    args.output = os.path.abspath(args.output)

    index = DocIndex(args.dictionary, args.postings)
    results = run_queries(index, args.queries)
    write_results(results, args.output)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='boolean retrieval ' +
                                     'assignment.')
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
