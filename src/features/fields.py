import patentfields
import math


class FieldFeatureBase(object):
    NAME = ''
    FIELD = None

    def score(self, val):
        raise NotImplementedError()

    def __call__(self, search, shared_obj):
        for doc_id, val in search.compound_index.value_for_field(self.FIELD):
            shared_obj.set_feature_score(self.NAME, doc_id, self.score(val))


class CitationCount(FieldFeatureBase):
    """Scores documents using the base-10 logarithm of their citation count."""
    NAME = 'citationcount'
    FIELD = patentfields.CITED_BY_COUNT

    def score(self, val):
        try:
            # Add one to the value since log(1) == 0
            val = int(val) + 1
            return math.log(val, 10)
        except ValueError:
            return 0
