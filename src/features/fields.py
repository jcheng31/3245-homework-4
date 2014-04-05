import patentfields
import math


class FieldFeatureBase(object):
    NAME = ''
    FIELD = None

    def score(self, val):
        raise NotImplementedError()

    def __call__(self, search, shared_obj):
        for doc_id, val in search.compound_index.value_for_field(self.FIELD):
            # Only add score for fields if object already has a score.
            if shared_obj.has_score(doc_id):
                shared_obj.set_feature_score(self.NAME, doc_id, self.score(val))

class CitationCount(FieldFeatureBase):
    NAME = 'citationcount'
    FIELD = patentfields.CITED_BY_COUNT

    def score(self, val):
        try:
            # Add one to the value since log(1) == 0
            val = int(val) + 1
            return math.log(val, 10)
        except ValueError:
            return 0
