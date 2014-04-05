import patentfields


class BooleanLayer(object):
    """Simple boolean search layer.

    Returns the set of doc_ids that are relevant to the search query using
    boolean retrieval
    """
    def __call__(self, search, shared_obj):
        for token in search.query_tokens:
            for idx in [patentfields.ABSTRACT, patentfields.TITLE]:
                matches = search.compound_index.postings_list(idx, token)
                for doc_id, _ in matches:
                    shared_obj.set_layer_score('BOOLEAN_LAYER', doc_id, 1)
