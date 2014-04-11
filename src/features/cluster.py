import collections

from helpers import cache


class ClusterBase(object):
    """Feature that clusters enum type fields.

    The intuition is that, for the relevant documents, if a particular enum
    appears more frequently among the documents that score well, this is a good
    signal for relevance.

    For each relevant document (so far), we take a rough estimate of the score
    add it to a bucket (based on that document's value in the specified field.)
    We then boost all documents (not only the currently relevant ones) based on
    which bucket they belong to.
    """
    INDEX = None

    @cache.naive_class_method_cache
    def get_cluster(self, compound_index, shared_obj, index):
        """Returns a dicionary with the aggregated/average scores for each
        field."""
        cluster = collections.defaultdict(lambda: 0)
        cluster_count = collections.defaultdict(lambda: 0)

        d = compound_index.dict_for_field(index)
        for doc_id, score_dict in shared_obj.doc_ids_to_scores.iteritems():
            val = d.get(doc_id)
            if val:
                # NOTE(michael): We use a not so arbitrary weight here (The
                # intuition is that is you score pretty well (roughly), your
                # enum value counts for a little more.
                # NOTE(michael): Ignore fields starting with 'Cluster' else we
                # get a unwanted compounding effect.
                weight = sum(v for k, v in score_dict.iteritems()
                    if not k.startswith('Cluster'))
                cluster[val] += weight
                cluster_count[val] += 1

        # Average the weights
        for k, v in cluster.iteritems():
            cluster[k] = v / cluster_count[k]

        return cluster

    def __call__(self, search, shared_obj):
        cluster = self.get_cluster(search.compound_index, shared_obj, self.INDEX)

        # Boost documents base on the cluster the belong to.
        for doc_id, val in search.compound_index.value_for_field(self.INDEX):
            score = cluster.get(val, 0)
            if score:
                shared_obj.set_feature_score(self.NAME, doc_id, score)


def cluster_feature_generator(index):
    """Dynamically generates a cluster subclass given an index."""
    name = 'Cluster' + index.replace(' ', '')
    return type(name, (ClusterBase,), {
        'NAME': name,
        'INDEX': index,
    })
