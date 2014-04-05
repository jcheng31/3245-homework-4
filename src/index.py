#!/env/bin/python
import argparse
import indexfields
import json
import math
import os
import patentfields
import utils

from parser import free_text


class IndexBuilder(object):
    guid = 0

    def __init__(self, dict_path, postings_path):
        self.dict_path = dict_path
        self.postings_path = postings_path
        self.m_file = {
            indexfields.DOC_GUID_MAP: dict(),
            indexfields.GUID_DOC_MAP: dict(),
            indexfields.INDICES: dict(),
            indexfields.FIELDS: dict(),
        }
        self.m_indices = dict()

    def get_guid(self, doc_id):
        """Return the guid for given doc_id.

        Normalise the doc_id by assigning it an integer guid for easier
        comparison. If the document has already been seen, we use its old guid.
        """
        all_docs = self.m_file[indexfields.DOC_GUID_MAP]
        if doc_id not in all_docs:
            guid = IndexBuilder.next_guid()
            all_docs[doc_id] = guid
            self.m_file[indexfields.GUID_DOC_MAP][guid] = doc_id
        return all_docs[doc_id]

    def add_value_for_field(self, val, doc_id, field):
        """Adds a simple field-value pair for a doc_id."""
        guid = self.get_guid(doc_id)

        if guid not in self.m_file[indexfields.FIELDS]:
            self.m_file[indexfields.FIELDS][guid] = {}

        self.m_file[indexfields.FIELDS][guid][field] = val

    def add_tokens_for_zone(self, tokens, doc_id, key):
        guid = self.get_guid(doc_id)

        # Create an index for the specified field (key) if it does not already
        # exist in the dictionary/postings file.
        indices = self.m_file[indexfields.INDICES]
        if key not in indices:
            indices[key] = {
                indexfields.INDEX_DOCS: set(),
                indexfields.INDEX_DICT: dict()
            }
        docs = indices[key][indexfields.INDEX_DOCS]
        dictionary = indices[key][indexfields.INDEX_DICT]

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
        indices = self.m_file[indexfields.INDICES]
        for key in indices:
            # We convert the document-set for each index to a sorted list so
            # that it can be natively json serialised.
            indices[key][indexfields.INDEX_DOCS] = \
                sorted(indices[key][indexfields.INDEX_DOCS])

            # Compute document frequency and inverse document frequency.
            index = indices[key]
            count = len(index[indexfields.INDEX_DOCS])
            for dict_key in index[indexfields.INDEX_DICT]:
                entries = index[indexfields.INDEX_DICT][dict_key]
                doc_freq = len(entries)
                idf = math.log(float(count) / doc_freq, 10)
                index[indexfields.INDEX_DICT][dict_key] = {
                    indexfields.TOKEN_DOC_FREQ: doc_freq,
                    indexfields.TOKEN_IDF: idf,
                    indexfields.TOKEN_ENTRIES: entries
                }

        with open(self.dict_path, 'w') as f:
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
    ZONES = [
        patentfields.TITLE,
        patentfields.ABSTRACT,
    ]

    FIELDS = [
        patentfields.CITED_BY_COUNT,
        patentfields.CITED_BY_WITHIN_THREE_YEARS,
        patentfields.CITED_BY_WITHIN_FIVE_YEARS,
    ]

    def __init__(self, doc_dir, indexer, free_text_tokenizer=None):
        # Normalize with trailing slash for consistency.
        if doc_dir[-1] != '/':
            doc_dir += '/'

        self.__doc_dir = doc_dir
        self.__indexer = indexer
        self.free_text_tokenizer = free_text_tokenizer or free_text

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
        # Process free text.
        for zone in self.ZONES:
            text = info.get(zone)
            if text:
                tokens = self.free_text_tokenizer(text)
                self.__indexer.add_tokens_for_zone(tokens, doc_id, zone)

        # Process fields.
        for field in self.FIELDS:
            val = info.get(field)
            if val:
                self.__indexer.add_value_for_field(val, doc_id, field)


def main(args):
    args.index = os.path.abspath(args.index)
    args.dictionary = os.path.abspath(args.dictionary)
    args.postings = os.path.abspath(args.postings)

    ib = IndexBuilder(args.dictionary, args.postings)
    dp = DirectoryProcessor(args.index, ib)
    dp.run()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Patsnap assignment - Index')
    parser.add_argument('-i', '--index', required=True,
                        help='directory of documents.')
    parser.add_argument('-d', '--dictionary', required=True,
                        help='dictionary file.')
    parser.add_argument('-p', '--postings', required=True,
                        help='postings file.')
    args = parser.parse_args()
    main(args)
