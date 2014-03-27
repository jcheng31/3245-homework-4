import patentfields


class BooleanLayer(object):
    """Simple boolean search layer.

    Returns the set of doc_ids that are relevant to the search query using
    boolean retrieval
    """
    def __call__(self, search, candidate_doc_ids):
        # Treat query as OR of the various terms in the query.
        retval = set()
        for token in search.query_tokens:
            for idx in [patentfields.ABSTRACT, patentfields.TITLE]:
                matches = search.compound_index.postings_list(idx, token)
                retval.update(set(elem[0] for elem in matches))
        return list(retval)
