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
                t[query]['fn'] = filename

            # results are in the format {{ query }}-qrels.txt
            results_path = os.path.join(queries_dir, query + '-qrels.txt')
            with open(results_path, 'r') as r:
                t[query]['results'] = {}
                t[query]['correct'] = []

                for entry in r:
                    entry = entry.strip()
                    if entry:
                        doc_id, score = entry.split('\t')
                        doc_id = doc_id.strip()
                        score = int(score)

                        t[query]['results'][doc_id] = score
                        if score == 1:
                            t[query]['correct'].append(doc_id)
    return t


def learn(compound_index):
    # We try to fit a function: `y = w1.x1 + w2.x2 ... wn.xn`
    # Where y values for known positive docs are 1 and 0 otherwise.
    t = training_data()
    for qname, q in t.iteritems():
        s = search.Search(q['query'], compound_index)
        q['search'] = s.execute()

    def f(coeff=None, dataset=0):
        """Returns the root mean squared deviation from the labelled scores."""
        q = training_data().values()[dataset]
        s = q['search']

        if coeff is not None:
            min_score = coeff[-1]
            s.override_proportion(min_score)
            # coeff = coeff[:-1]
            # weights = coeff[:len(coeff)/2]
            # thresholds = coeff[len(coeff)/2:]
            # s.override_features_weights(weights)
            # s.override_features_thresholds(thresholds)

        results = s.results()
        correct = 0
        count = 0
        unknown = 0
        beta = 2.0
        total_positive = len(q['correct'])

        precision = []
        recall = []
        f = []

        for r in results:
            count += 1
            if q['results'].get(r) == 1:
                correct += 1
            elif r not in q['results']:
                unknown += 1
                continue

            total_known = count - unknown
            if total_known == 0:
                p = 0
                r = 0
            else:
                p = float(correct) / total_known
                r = float(correct) / total_positive

            precision.append(p)
            recall.append(r)

            f_base = (beta**2 * precision[-1]) + recall[-1]
            if f_base == 0:
                f_val = 0
            else:
                f_val = ((beta**2 + 1) * precision[-1] * recall[-1]) / f_base
            f.append(f_val)

        if len(f) == 0:
            avg_p = 0
            avg_r = 0
            avg_f = 0
        else:
            avg_p = sum(precision) / len(precision)
            avg_r = sum(recall) / len(recall)
            avg_f = sum(f) / len(f)

        return avg_f

    def train_f(weights):
        total = 0
        for idx in xrange(4):
            val = f(weights, dataset=idx)
            total += (1 - val)
        return total

    starting_coeffs = [1]

    print '# Root mean squared with current weights'
    print 'Dataset 0:', f(None, 0)
    print 'Dataset 1:', f(None, 1)
    print 'Dataset 2:', f(None, 2)
    print 'Dataset 3:', f(None, 3)
    print train_f(None)


    # print '# Root mean squared with new weights (fmin_powell)'
    # result = scipy.optimize.fmin_powell(f, list(starting_coeffs))
    # print result, train_f(result)
    # for idx in xrange(4):
    #     print idx, f(result, dataset=idx)

    print '# Root mean squared with new weights (downhill simplex)'
    result = scipy.optimize.fmin(train_f, starting_coeffs)
    print result, train_f(result)
    for idx in xrange(4):
        print idx, f(result, dataset=idx)

    print '# Root mean squared with new weights (BFGS)'
    result = scipy.optimize.fmin_bfgs(train_f, starting_coeffs)
    print result, train_f(result)
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
