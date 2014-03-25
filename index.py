#!/env/bin/python
import os
import math
import json
import argparse
import textprocessors
import utils


class IndexBuilder(object):
    guid = 0

    def __init__(self, dict_path, postings_path):
        self.dict_path = dict_path
        self.postings_path = postings_path
        self.m_file = {
            'doc_guid': dict(),
            'guid_doc': dict(),
            'indices': dict()
        }
        self.m_indices = dict()

    def add_tokens_for_key(self, tokens, doc_id, key):
        # Normalise the doc_id by assigning it an integer guid for easier
        # comparison. If the document has already been seen, we use its old
        # guid.
        all_docs = self.m_file['doc_guid']
        if doc_id not in all_docs:
            guid = IndexBuilder.next_guid()
            all_docs[doc_id] = guid
            self.m_file['guid_doc'][guid] = doc_id
        guid = all_docs[doc_id]

        # Create an index for the specified field (key) if it does not already
        # exist in the dictionary/postings file.
        indices = self.m_file['indices']
        if key not in indices:
            indices[key] = {
                'docs': set(),
                'dictionary': dict()
            }
        docs = indices[key]['docs']
        dictionary = indices[key]['dictionary']

        # Within the index for the specified field (key), we add the document's
        # guid to the set of documents that occur in that index.
        docs.add(guid)

        # Finally, we iterate through each token seen in that document and
        # build a list of (guid, term_frequency)-tuples.
        tf = self.__compute_term_frequencies(tokens)
        for term in tf:
            _tuple = (guid, tf[term])
            if term in dictionary:
                dictionary[term].append(_tuple)
            else:
                dictionary[term] = [_tuple]

    def serialize(self, pretty=False):
        indices = self.m_file['indices']
        for key in indices:
            # We convert the document-set for each index to a sorted list so that
            # it can be natively json serialised.
            indices[key]['docs'] = sorted(indices[key]['docs'])

            # Compute document frequency and inverse document frequency.
            index = indices[key]
            count = len(index['docs'])
            for dict_key in index['dictionary']:
                entries = index['dictionary'][dict_key]
                doc_freq = len(entries)
                idf = math.log(float(count) / doc_freq, 10)
                index['dictionary'][dict_key] = {
                    'df': doc_freq,
                    'idf': idf,
                    'entries': entries
                }

        with open(self.dict_path, 'w') as f:
            if pretty:
                json.dump(self.m_file, f, indent=2)
            else:
                json.dump(self.m_file, f)

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

    @staticmethod
    def next_guid():
        val = IndexBuilder.guid
        IndexBuilder.guid += 1
        return val


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
            patent_info = utils.xml_file_to_dict(full_path)
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
