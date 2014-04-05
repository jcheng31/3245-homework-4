import patentfields


class Boolean(object):
    """Simple boolean search feature.

    Assigns a score of 1 if any search term is present in the document.
    """
    def __call__(self, search, shared_obj):
        for token in search.query_tokens:
            for idx in [patentfields.ABSTRACT, patentfields.TITLE]:
                matches = search.compound_index.postings_list(idx, token)
                for doc_id, _ in matches:
                    shared_obj.set_layer_score('BOOLEAN_LAYER', doc_id, 1)
