import collections
import patentfields
import utils

from helpers import cache
from vsmutils import *


class VSMBase(object):
    """Base VSM search feature."""
    NAME = ''

    def idf(self, term, compound_index):
        raise NotImplementedError()

    def query_tokens(self, search):
        raise NotImplementedError()

    def matches(self, term, compound_index):
        raise NotImplementedError()

    def __call__(self, search, shared_obj):
        compound_index = search.compound_index

        query_tokens = self.query_tokens(search)
        query_tf = collections.Counter(query_tokens)
        query_stems = map(lambda x: x.stem, set(query_tokens))
        query_terms_sorted = sorted(query_stems)

        # NOTE(michael): Do the idf weighting on the query vector so we only do
        # it once. (similar to doing this on the tf values of individual
        # documents).
        query_vector = [logtf(query_tf[term]) * self.idf(term, compound_index)
            for term in query_terms_sorted]
        unit_query_vector = list(unit_vector(query_vector))

        # Get the tfs of the docs for each of the query terms.
        results = collections.defaultdict(dict)
        for term in query_tokens:
            for doc_id, term_frequency in self.matches(term, compound_index):
                results[doc_id][term.stem] = term_frequency

        # Calculate the document score.
        for doc_id, tfs in results.iteritems():
            doc_vector = [tfs.get(term, 0) for term in query_terms_sorted]
            score = dot_product(query_vector, unit_vector(doc_vector))
            shared_obj.set_feature_score(self.NAME, doc_id, score)

    def __get_stem_unstemmed_pairs(self, index, search):
        tokens = search.get_tokens_for(self.INDEX)
        if self.INDEX == patentfields.TITLE:
            unstemmed = search.query_title
        else:
            unstemmed = search.query_description

        Token = collections.namedtuple('Token', 'stem unstemmed')
        return map(Token, tokens, unstemmed)


class VSMSingleField(VSMBase):
    """VSM feature using a single index."""
    INDEX = None

    def idf(self, term, compound_index):
        return compound_index.inverse_document_frequency(self.INDEX, term)

    def query_tokens(self, search):
       return self.__get_stem_unstemmed_pairs(self.INDEX, search)

    def matches(self, term, compound_index):
        return compound_index.postings_list(self.INDEX, term.stem)


class VSMSingleFieldMinusStopwords(VSMSingleField):
    """VSM feature using a single field, removing stopwords."""
    def query_tokens(self, search):
        query_tokens = super(VSMSingleFieldMinusStopwords,
            self).query_tokens(search)
        return utils.without_stopwords(query_tokens)


class VSMTitle(VSMSingleField):
    NAME = 'VSM_Title'
    INDEX = patentfields.TITLE


class VSMAbstract(VSMSingleField):
    NAME = 'VSM_Abstract'
    INDEX = patentfields.ABSTRACT


class VSMTitleMinusStopwords(VSMSingleFieldMinusStopwords):
    NAME = 'VSM_Title_Minus_Stopwords'
    INDEX = patentfields.TITLE


class VSMAbstractMinusStopwords(VSMSingleFieldMinusStopwords):
    NAME = 'VSM_Abstract_Minus_Stopwords'
    INDEX = patentfields.ABSTRACT


class VSMMultipleFields(VSMBase):
    """VSM feature using multiple indices."""
    ZONES = []

    def idf(self, term, compound_index):
        # HACK(michael): Calculate the idf from the idfs of the fields.
        documents_with_term = set()
        for idx in self.ZONES:
            for doc_id, _ in compound_index.postings_list(idx, term):
                documents_with_term.add(doc_id)
        document_freq = len(documents_with_term)
        documents_in_index = self.number_of_docs_in_indices(compound_index)
        return idf(documents_in_index, document_freq)

    @cache.naive_class_method_cache
    def number_of_docs_in_indices(self, compound_index):
        documents_in_index = set()
        for idx in self.ZONES:
            for doc_id in compound_index.documents_in_index(idx):
                documents_in_index.add(doc_id)
        return len(documents_in_index)

    def query_tokens(self, search):
        tokens = []
        for idx in self.ZONES:
            tokens.extend(self.__get_stem_unstemmed_pairs(idx, search))
        return tokens

    def matches(self, term, compound_index):
        results = collections.defaultdict(lambda: 0)
        for idx in self.ZONES:
            for doc_id, term_freq in compound_index.postings_list(idx, term):
                results[doc_id] += term_freq
        return results.iteritems()


class VSMMultipleFieldsMinusStopwords(VSMMultipleFields):
    """VSM feature using multiple indices, removing stopwords."""
    def query_tokens(self, search):
        query_tokens = super(VSMMultipleFieldsMinusStopwords,
            self).query_tokens(search)
        return utils.without_stopwords(query_tokens)


class VSMTitleAndAbstract(VSMMultipleFields):
    NAME = 'VSM_Title_and_Abstract'
    ZONES = [patentfields.TITLE, patentfields.ABSTRACT]


class VSMTitleAndAbstractMinusStopwords(VSMMultipleFieldsMinusStopwords):
    NAME = 'VSM_Title_and_Abstract_Minus_Stopwords'
    ZONES = [patentfields.TITLE, patentfields.ABSTRACT]
