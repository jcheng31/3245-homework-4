import collections

from features.vsm.vsmutils import *


class VSMBase(object):
    """Base VSM search feature.

    The general idea is to use a vector space model (VSM) to score documents.
    We extend this base class in several ways to provide several different VSM
    scores (which operate on different indices etc.).
    """
    NAME = ''

    def idf(self, term):
        """Given a term, returns the IDF score for that term in the index."""
        raise NotImplementedError()

    def query_tokens(self):
        """Returns a list of tokens for the query."""
        raise NotImplementedError()

    def matches(self, term):
        """Returns a list of postings for the given term.

        Each posting is a (doc_id, term_frequency) pair."""
        raise NotImplementedError()

    def __call__(self, search, shared_obj):
        # Assign instance properties (so these are accessible in the other
        # methods.)
        self.search = search
        self.compound_index = search.compound_index

        query_tokens = self.query_tokens()
        query_tf = collections.Counter(query_tokens)
        query_terms_sorted = sorted(set(query_tokens))

        # NOTE(michael): Do the idf weighting on the query vector so we only do
        # it once. (similar to doing this on the tf values of individual
        # documents).
        query_vector = [logtf(query_tf[term]) * self.idf(term)
            for term in query_terms_sorted]
        unit_query_vector = list(unit_vector(query_vector))

        # Get the tfs of the docs for each of the query terms.
        results = collections.defaultdict(dict)
        for term in query_tokens:
            for doc_id, term_frequency in self.matches(term):
                results[doc_id][term] = term_frequency

        # Calculate the document score.
        for doc_id, tfs in results.iteritems():
            doc_vector = [tfs.get(term, 0) for term in query_terms_sorted]
            score = dot_product(unit_query_vector, unit_vector(doc_vector))
            shared_obj.set_feature_score(self.NAME, doc_id, score)
