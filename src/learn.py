import argparse
import compoundindex
import json
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


def learn(compound_index):
    # We try to fit a function: `y = w1.x1 + w2.x2 ... wn.xn`
    # Where y values for known positive docs are 1 and 0 otherwise.
    t = training_data()
    for qname, q in t.iteritems():
        s = search.Search(q['query'], compound_index)
        q['search'] = s.execute()

    def f(weights=None, dataset=0):
        """Returns the root mean squared deviation from the labelled scores."""
        q = training_data().values()[dataset]
        s = q['search']

        if weights is not None:
            s.override_features_weights(weights)

        r = s.results(verbose=True)

        total_deviation = 0
        for doc_id, desired_score in q['results'].iteritems():
            score = r.get(doc_id, [0])[0]

            if desired_score == 0:
                deviation = max(desired_score, score) - desired_score
            else:
                deviation = desired_score - min(desired_score, score)

            total_deviation += deviation**2

        return float(total_deviation) / len(q['results'])

    print '# Root mean squared with current weights'
    print 'Dataset 0:', f(None, 0)
    print 'Dataset 1:', f(None, 1)
    print 'Dataset 2:', f(None, 2)
    print 'Dataset 3:', f(None, 3)


    def train_f(weights):
        # train on all datasets
        total = 0
        count = 0
        for idx in xrange(4):
            val = f(weights, dataset=idx)
            total += val * training_data().values()[idx]['results']
            count += training_data().values()[idx]['results']
        return total / count

    starting_coeffs = [1] * len(search.Search.FEATURES)

    print '# Root mean squared with new weights (fmin_powell)'
    result = scipy.optimize.fmin_powell(f, list(starting_coeffs))
    print result
    for idx in xrange(4):
        print idx, f(result, dataset=idx)

    print '# Root mean squared with new weights (downhill simplex)'
    result = scipy.optimize.fmin(f, starting_coeffs)
    print result
    for idx in xrange(4):
        print idx, f(result, dataset=idx)

    print '# Root mean squared with new weights (BFGS)'
    result = scipy.optimize.fmin_bfgs(f, starting_coeffs)
    print result
    for idx in xrange(4):
        print idx, f(result, dataset=idx)


def main(args):
    dictionary_file = os.path.abspath(args.dictionary)
    with open(dictionary_file, 'r') as f:
        json_obj = json.load(f)
    compound_index = compoundindex.CompoundIndex(json_obj)
    learn(compound_index)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Patsnap assignment - Learn')
    parser.add_argument('-d', '--dictionary', help='dictionary file.',
                        default='run/dictionary.txt')
    args = parser.parse_args()
    main(args)
