import collections

from features.vsm.vsmutils import *


class VSMBase(object):
    """Base VSM search feature.

    The general idea is to use a vector space model (VSM) to score documents.

    We extend this base class in several ways to provide several different VSM
    scores (which operate on different indices etc.). Each subclass overrides
    (among other methods) `query_tokens` and `matches` to specify the query
    and field for the VSM.

    At a high-level, each VSM feature has a query (returned by `query_tokens`):

        [A, B, C]

    and a call to matches (with a term) should return a postings list:

        self.matches(A) => [(d1, tf), (d2, tf) ... ]

    Through a simple class hierachy, we are able to create VSM features for:

        - query::title -> document::title
        - query::title (less stopwords) -> document::title
        - query::title (only nouns) -> document::title
        - query::description -> document::abstract
        - ...
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
        # methods, allowing subclasses to defined more complex behavior than
        # is specified here.)
        self.search = search
        self.compound_index = search.compound_index

        # Process query (to get the dimensions of the VSM and the
        # unit_query_vector.)
        query_tokens = self.query_tokens()
        query_tf = collections.Counter(query_tokens)
        query_terms_sorted = sorted(set(query_tokens))
        # NOTE(michael): Do the idf weighting on the query vector so we only do
        # it once. (similar to doing this on the tf values of individual
        # documents).
        query_vector = [logtf(query_tf[term]) * self.idf(term)
            for term in query_terms_sorted]
        unit_query_vector = list(unit_vector(query_vector))

        # Get the term frequencies of the docs for each of the dimensions.
        results = collections.defaultdict(dict)
        for term in query_tokens:
            for doc_id, term_frequency in self.matches(term):
                results[doc_id][term] = term_frequency

        # Calculate the document score.
        for doc_id, tfs in results.iteritems():
            doc_vector = [tfs.get(term, 0) for term in query_terms_sorted]
            doc_unit_vector = unit_vector(doc_vector)
            score = dot_product(unit_query_vector, doc_unit_vector)

            # Set the score on the shared search object.
            shared_obj.set_feature_score(self.NAME, doc_id, score)
