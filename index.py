#!/env/bin/python
import os
import argparse
import textprocessors
from patent import Patent

try:
    import ujson as json_impl
except ImportError:
    import json as json_impl
    print 'ujson not found, using native json'


class IndexBuilder(object):
    def __init__(self, dict_path, postings_path):
        self.dict_path = dict_path
        self.postings_path = postings_path
        self.m_indices = dict()

    def add_tokens_for_key(self, tokens, doc_id, key):
        if key not in self.m_indices:
            self.m_indices[key] = {
                'docs': set(),
                'dictionary': dict()
            }

        docs = self.m_indices[key]['docs']
        dictionary = self.m_indices[key]['dictionary']

        docs.add(doc_id)
        tf = self.__compute_term_frequencies(tokens)
        for term in tf:
            _tuple = (doc_id, tf[term])
            if term in dictionary:
                dictionary[term].append(_tuple)
            else:
                dictionary[term] = [_tuple]

    def serialize(self):
        for key in self.m_indices:
            self.m_indices[key]['docs'] = sorted(self.m_indices[key]['docs'])
        with open(self.dict_path, 'w') as f:
            json_impl.dump(self.m_indices, f)

    def __compute_term_frequencies(self, tokens):
        """
        Computes document frequencies.
        """
        tf = dict()
        for w in tokens:
            if w in tf:
                tf[w] += 1
            else:
                tf[w] = 1
        return tf


class DirectoryProcessor(object):
    def __init__(self, doc_dir, indexer, extract_fields):
        # Normalize with trailing slash for consistency.
        if doc_dir[-1] != '/':
            doc_dir += '/'

        self.__doc_dir = doc_dir
        self.__indexer = indexer
        self.__extract_fields = extract_fields

    def run(self):
        for filename in os.listdir(self.__doc_dir):
            doc_id, extension = os.path.splitext(filename)
            if extension.lower() != '.xml':
                print 'Ignoring file: {} Reason: Not an XML document.'\
                      .format(filename)
                continue

            full_path = self.__doc_dir + filename
            patent_info = Patent.from_file(full_path)
            self.__process_patent(doc_id, patent_info)

        self.__indexer.serialize()

    def __process_patent(self, doc_id, info):
        for field in self.__extract_fields:
            text = info.get(field, None)
            if text:
                tokens = self.__extract_fields[field](text)
                self.__indexer.add_tokens_for_key(tokens, doc_id, field)


def main(args):
    args.index = os.path.abspath(args.index)
    args.dictionary = os.path.abspath(args.dictionary)
    args.postings = os.path.abspath(args.postings)

    ib = IndexBuilder(args.dictionary, args.postings)
    dp = DirectoryProcessor(args.index, ib, textprocessors.extract_fields)
    dp.run()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='boolean retrieval \
                                     assignment.')
    parser.add_argument('-i', '--index', type=str, help='directory of \
                        of documents.', required=True)
    parser.add_argument('-d', '--dictionary', type=str, help='dictionary \
                        file.', default='dictionary.txt')
    parser.add_argument('-p', '--postings', type=str, help='postings file.',
                        default='postings.txt')
    args = parser.parse_args()
    main(args)
