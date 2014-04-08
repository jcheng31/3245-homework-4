import collections
import patentfields


class RelationalFeatureBase(object):
    FIELD = None

    def __call__(self, search, shared_obj):
        relational_score = collections.defaultdict(lambda: 0)

        d = search.compound_index.dict_for_field(self.FIELD)
        for doc_id, score_dict in shared_obj.doc_ids_to_scores.iteritems():
            related_docs = d.get(doc_id)
            if related_docs:
                # NOTE(michael): We use a not so arbitrary weight here (The
                # intuition is that is you score pretty well (roughly), your
                # enum value counts for a little more.
                weight = sum(v for k, v in score_dict.iteritems())

                related_docs = related_docs.split('|')
                for related in related_docs:
                    related = related.strip()
                    doc_id = \
                        search.compound_index.guid_for_document_name(related)
                    # Related doc might not be in our corpus.
                    if doc_id:
                        relational_score[doc_id] += weight

        for doc_id, score in relational_score.iteritems():
            shared_obj.set_feature_score(self.NAME, doc_id, score)


class Citations(RelationalFeatureBase):
    NAME = 'Cites'
    FIELD = patentfields.CITES


class FamilyMembers(RelationalFeatureBase):
    NAME = 'FamilyMembers'
    FIELD = patentfields.FAMILY_MEMBERS
