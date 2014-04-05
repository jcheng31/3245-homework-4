import collections
import patentfields

from vsmutils import *


class VectorSpaceModelBase(object):
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
        query_terms_sorted = sorted(set(query_tokens))

        # NOTE(michael): Do the idf weighting on the query vector so we only do
        # it once. (similar to doing this on the tf values of individual
        # documents).
        query_vector = [logtf(query_tf[term]) * self.idf(term, compound_index)
            for term in query_terms_sorted]
        unit_query_vector = list(unit_vector(query_vector))

        # Get the tfs of the docs for each of the query terms.
        results = collections.defaultdict(dict)
        for term in query_terms_sorted:
            for doc_id, term_frequency in self.matches(term, compound_index):
                results[doc_id][term] = term_frequency

        # Calculate the document score.
        for doc_id, tfs in results.iteritems():
            doc_vector = [tfs.get(term, 0) for term in query_terms_sorted]
            score = dot_product(query_vector, unit_vector(doc_vector))
            shared_obj.set_feature_score(self.NAME, doc_id, score)


class VectorSpaceModelSingleField(VectorSpaceModelBase):
    """VSM feature using a single index."""
    INDEX = None

    def idf(self, term, compound_index):
        return compound_index.inverse_document_frequency(self.INDEX, term)

    def query_tokens(self, search):
        return search.get_tokens_for(self.INDEX)

    def matches(self, term, compound_index):
        return compound_index.postings_list(self.INDEX, term)


class VectorSpaceModelTitle(VectorSpaceModelSingleField):
    NAME = 'VSM_Title'
    INDEX = patentfields.TITLE


class VectorSpaceModelAbstract(VectorSpaceModelSingleField):
    NAME = 'VSM_Abstract'
    INDEX = patentfields.ABSTRACT


class VectorSpaceModelMultipleFields(VectorSpaceModelBase):
    """VSM feature using multiple indices."""
    INDICES = []

    def idf(self, term, compound_index):
        # HACK(michael): Calculate the idf from the idfs of the fields.
        documents_with_term = set()
        for idx in self.INDICES:
            for doc_id, _ in compound_index.postings_list(idx, term):
                documents_with_term.add(doc_id)
        document_freq = len(documents_with_term)
        documents_in_index = self.number_of_docs_in_indices(compound_index)
        return math.log(float(documents_in_index) / document_freq, 10)

    def number_of_docs_in_indices(self, compound_index):
        documents_in_index = set()
        for idx in self.INDICES:
            for doc_id in compound_index.documents_in_index(idx):
                documents_in_index.add(doc_id)
        return len(documents_in_index)

    def query_tokens(self, search):
        tokens = []
        for idx in self.INDICES:
            tokens.extend(search.get_tokens_for(idx))
        return tokens

    def matches(self, term, compound_index):
        results = collections.defaultdict(lambda: 0)
        for idx in self.INDICES:
            for doc_id, term_freq in compound_index.postings_list(idx, term):
                results[doc_id] += term_freq
        return results.iteritems()


class VectorSpaceModelTitleAndAbstract(VectorSpaceModelMultipleFields):
    NAME = 'VSM_Title_and_Abstract'
    INDICES = [patentfields.TITLE, patentfields.ABSTRACT]
