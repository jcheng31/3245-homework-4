import json
import indexfields


class CompoundIndex(object):
    def __init__(self, dict_path):
        self.__path = dict_path
        with open(self.__path, 'r') as f:
            self.__m_file = json.load(f)

        self.__gd_map = self.__m_file[indexfields.GUID_DOC_MAP]
        self.__dg_map = self.__m_file[indexfields.DOC_GUID_MAP]
        self.__indices = self.__m_file[indexfields.INDICES]
        self.__fields = self.__m_file[indexfields.FIELDS]

        self.__remap()

    def __str__(self):
        return 'CompoundIndex (Loaded Dictionary: {})'.format(self.____path)

    def __remap(self):
        """Remaps keys to ints (JSON keys have to be strings.)"""
        # Keys in JSON have to be strings, and our GUIDs are implicitly cast
        # to strings on serialisation. We re-parse them into integer types to
        # recover ease of comparison.
        self.__m_file[indexfields.GUID_DOC_MAP] = {
            int(key): self.__gd_map[key] for key in self.__gd_map
        }

    def indices(self):
        """
        Returns a list of indexed fields in this compound index.
        """
        return sorted(self.__indices.keys())

    def document_name_for_guid(self, guid):
        """
        Returns the document name on the disk for a given guid.
        """
        return self.__gd_map.get(guid, None)

    def guid_for_document_name(self, name):
        """
        Returns the guid for a given document name.
        """
        return self.__dg_map.get(name, None)

    def documents_in_index(self, index_name):
        """
        Returns a list of documents seen in a given index.

        If the specified index does not exist, returns an empty list.
        """
        if index_name not in self.__indices:
            return []
        else:
            return self.__indices[index_name][indexfields.INDEX_DOCS]

    def value_for_field(self, field):
        """
        Returns a list of (guid, fieid_value) for the given field.
        """
        retval = []
        for guid, fields in self.__fields.iteritems():
            if field in fields:
                retval.append(guid, fields.get(field))
        return retval

    def terms_in_index(self, index_name):
        """
        Returns a list of terms seen in a given index.

        If the specified index does not exist, returns an empty list.
        """
        if index_name not in self.__indices:
            return []
        else:
            index = self.__indices[index_name]
            return sorted(index[indexfields.INDEX_DICT].keys())

    def term_count_for_index(self, index_name):
        """
        Returns the number of terms in a given index.

        If the specified index does not exist, returns 0.
        """
        if index_name not in self.__indices:
            return 0
        else:
            index = self.__indices[index_name]
            return len(index[indexfields.INDEX_DICT].keys())

    def document_frequency(self, index_name, term):
        """
        Returns the document frequency for a term in the given index.

        If the specified term does not exist in the index, returns 0.
        """
        if index_name not in self.__indices:
            raise KeyError('Index: {} not recognized'.format(index_name))
        assert index_name in self.__indices

        dictionary = self.__indices[index_name][indexfields.INDEX_DICT]
        if term not in dictionary:
            return 0
        else:
            return dictionary[term][indexfields.TOKEN_DOC_FREQ]

    def inverse_document_frequency(self, index_name, term):
        """
        Returns the inverse document frequency for a term in the given index.

        If the specified term does not exist in the index, returns 0.
        """
        if index_name not in self.__indices:
            raise KeyError('Index: {} not recognized'.format(index_name))
        assert index_name in self.__indices

        dictionary = self.__indices[index_name][indexfields.INDEX_DICT]
        if term not in dictionary:
            return 0
        else:
            return dictionary[term][indexfields.TOKEN_IDF]

    def postings_list(self, index_name, term, use_doc_names=False):
        """
        Returns the postings list for a term in the given index.

        The postings list is a list of (guid, term_freq)-tuples.

        If use_doc_names is True, a list of (document_name, term_freq)-tuples
        is returned instead.
        """
        if index_name not in self.__indices:
            raise KeyError('Index: {} not recognized'.format(index_name))
        assert index_name in self.__indices

        dictionary = self.__indices[index_name][indexfields.INDEX_DICT]
        if term not in dictionary:
            return []
        else:
            postings = dictionary[term][indexfields.TOKEN_ENTRIES]
            result = []
            for entry in postings:
                assert len(entry) == 2
                guid, tf = entry[0], entry[1]
                if use_doc_names:
                    guid = self.document_name_for_guid(guid)
                result.append((guid, tf))
            return result
