import argparse
import compoundindex
import os
import scipy.optimize
import search
import utils

from helpers import cache


@cache.cached_function()
def training_data(queries_dir='queries'):
    t = {}

    for filename in os.listdir(queries_dir):
        query, extension = os.path.splitext(filename)
        # NOTE(michael): queries are in xml format
        if extension.lower() == '.xml':
            with open(os.path.join(queries_dir, filename), 'r') as q:
                t[query] = {}
                t[query]['query'] = q.read()

            # results are in the format {{ query }}-qrels.txt
            results_path = os.path.join(queries_dir, query + '-qrels.txt')
            with open(results_path, 'r') as r:
                t[query]['results'] = {}

                for entry in r:
                    entry = entry.strip()
                    if entry:
                        doc_id, score = entry.split('\t')
                        score = int(score)
                    t[query]['results'][doc_id] = score
    return t


# def learn(compound_index):
#     # We try to fit a function: `y = w1.x1 + w2.x2 ... wn.xn`
#     # Where y values for known positive docs = 10 and y values for known
#     # negative docs = 0.
#     negative_score_bound = 0
#     positive_score_bound = 1
#
#     # Optimise using first dataset.
#     for data in TRAINING_DATA:
#         query_xml = data['query_xml'].strip()
#         s = search.Search(query_xml, compound_index)
#         # Override all weights to be 1.
#         s.override_features_weights([1] * len(search.Search.FEATURES))
#         results = s.execute(verbose=True)
#
#         y = []
#         x = []
#         for result in results:
#             if result[-1] in data['positive']:
#                 y.append(positive_score_bound)
#
#             if result[-1] in data['negative']:
#                 y.append(negative_score_bound)
#
#             x.append(result[1])
#
#         data['y'] = y
#         data['x'] = x
#
#     def f(weights, dataset=0):
#         """Returns the root mean squared deviation from the positive/negative
#         bounds specified above.
#
#         """
#         x = TRAINING_DATA[dataset]['x']
#         y = TRAINING_DATA[dataset]['y']
#
#         total_deviation = 0
#         for idx, desired_score in enumerate(y):
#             predictor_values = x[idx]
#             score = utils.dot_product(weights, predictor_values)
#
#             if desired_score == positive_score_bound:
#                 deviation = desired_score - min(desired_score, score)
#             else:
#                 deviation = max(desired_score, score) - desired_score
#
#             total_deviation += deviation**2
#
#         return float(total_deviation) / len(y)
#
#     print '# Root mean squared with current weights'
#     print 'Dataset 0:', f(s.old_features_weights, dataset=0)
#     print 'Dataset 1', f(s.old_features_weights, dataset=1)
#
#     print '# Root mean squared with new weights (fmin_powell)'
#     result = scipy.optimize.fmin_powell(f, [1] * len(search.Search.FEATURES))
#     print result
#     print 'Dataset 0', f(result, dataset=0)
#     print 'Dataset 1', f(result, dataset=1)
#
#     print '# Root mean squared with new weights (downhill simplex)'
#     result = scipy.optimize.fmin(f, [1] * len(search.Search.FEATURES))
#     print result
#     print 'Dataset 0', f(result, dataset=0)
#     print 'Dataset 1', f(result, dataset=1)
#
#     print '# Root mean squared with new weights (BFGS)'
#     result = scipy.optimize.fmin_bfgs(f, [1] * len(search.Search.FEATURES))
#     print result
#     print 'Dataset 0', f(result, dataset=0)
#     print 'Dataset 1', f(result, dataset=1)
#
#
# def evaluate(weights=None):
#     for data in TRAINING_DATA:
#         query_xml = data['query_xml'].strip()
#         s = search.Search(query_xml, compound_index)
#         if weights:
#             s.override_features_weights(weights)
#         results = s.execute(verbose=True)
#
#         for result in results:
#             if result[-1] in data['positive']:
#                 y.append(positive_score_bound)
#
#             if result[-1] in data['negative']:
#                 y.append(negative_score_bound)
#
#
# def main(args):
#     dictionary_file = os.path.abspath(args.dictionary)
#     compound_index = compoundindex.CompoundIndex(dictionary_file)
#     learn(compound_index)

def main(args):
    training_data()



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Patsnap assignment - Learn')
    parser.add_argument('-d', '--dictionary', help='dictionary file.',
                        default='run/dictionary.txt')
    args = parser.parse_args()
    main(args)
