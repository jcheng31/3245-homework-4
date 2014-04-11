import collections
import patentfields
import utils

from helpers import cache
from features.vsm import base
from features.vsm.vsmutils import *


class VSMMultipleFields(base.VSMBase):
    """VSM feature using multiple indices."""
    ZONES = []

    def idf(self, term):
        # HACK(michael): Calculate the idf from the idfs of the fields.
        documents_with_term = set()
        for idx in self.ZONES:
            for doc_id, _ in self.compound_index.postings_list(idx, term):
                documents_with_term.add(doc_id)
        document_freq = len(documents_with_term)
        documents_in_index = self.number_of_docs_in_indices()
        return idf(documents_in_index, document_freq)

    @cache.naive_class_method_cache
    def number_of_docs_in_indices(self):
        documents_in_index = set()
        for idx in self.ZONES:
            for doc_id in self.compound_index.documents_in_index(idx):
                documents_in_index.add(doc_id)
        return len(documents_in_index)

    def query_tokens(self):
        tokens = []
        for idx in self.ZONES:
            tokens.extend(self.search.get_tokens_for(idx))
        return tokens

    def matches(self, term):
        results = collections.defaultdict(lambda: 0)
        for idx in self.ZONES:
            for doc_id, term_freq in \
                    self.compound_index.postings_list(idx, term):
                results[doc_id] += term_freq
        return results.iteritems()


class VSMMultipleFieldsMinusStopwords(VSMMultipleFields):
    """VSM feature using multiple indices, removing stopwords."""
    def query_tokens(self):
        query_tokens = super(VSMMultipleFieldsMinusStopwords,
            self).query_tokens()
        return utils.without_stopwords(query_tokens)


class VSMTitleAndAbstract(VSMMultipleFields):
    NAME = 'VSM_Title_and_Abstract'
    ZONES = [patentfields.TITLE, patentfields.ABSTRACT]


class VSMTitleAndAbstractMinusStopwords(VSMMultipleFieldsMinusStopwords):
    NAME = 'VSM_Title_and_Abstract_Minus_Stopwords'
    ZONES = [patentfields.TITLE, patentfields.ABSTRACT]
