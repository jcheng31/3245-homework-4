import argparse
import compoundindex
import os
import search
import scipy.optimize
import utils


# TODO(michael): Refactor this to another file. (Possibly get new data from the
# trial runs?)
TRAINING_DATA = [
    {
        'query_xml': """\
            <?xml version="1.0" ?>
            <query>
                <title>
                  Washers that clean laundry with bubbles
                </title>
                <description>
                  Relevant documents will describe washing technologies that clean or
                  induce using bubbles, foam, by means of vacuuming, swirling, inducing
                  flow or other mechanisms.
                </description>
            </query>""",
        'positive': [
            "US20080250823A1", "EP1918442A2", "US5253080", "US20080016626A1",
            "US20070289612A1", "EP2372006A2", "EP1918442A2", "US6170303",
            "US5295373", "EP0735178A1", "US20100037661A1", "US20120097752A1",
            "US5590551", "US20100236000A1", "WO2010055701A1", "US20110191965A1",
            "EP2298978A2", "US20090241267A1", "WO2011066805A1", "EP1546447A1",
            "US5432969", "WO2011015457A1", "US20080099052A1", "EP1918441A1",
        ],
        'negative': [
            "US20050189439A1", "US7131597", "US6427704", "EP0698680B1",
            "WO2008038763A1", "WO2011104633A3", "WO2010140775A2",
            "US20070119987A1", "US4889620", "WO1997028909A1", "US20070175502A1",
            "WO2000028129A1", "EP2402494A1", "US5017343", "US8076117",
            "US20020033550A1", "WO2003066229A1", "US5170942", "US20120118023A1",
            "EP2194567B1", "US20110315796A1", "US4974375", "EP0266476A2",
            "US4157922", "EP2361689A1",
        ]
    },
    {
        'query_xml': """\
            <?xml version="1.0" ?>
            <query>
                <title>
                  Biological Waste Water Treatment
                </title>
                <description>
                  Relevant documents will describe waste water treatment using
                  any biological means.  Forms of treatment include using
                  bacteria or microorganisms to digest, treat, react or
                  decompose impurities and pollutants.
                </description>
            </query>""",
        'positive': [
            "US7442313", "US7695623", "US7718063", "US7501060", "US7497948",
            "US7645382", "US7699976", "US7871525", "US7686956", "US7378022",
            "US7887705", "US7485231", "US7658850", "US7784769", "US7611638",
            "US8052872", "US7407577", "US7485228", "US7425261", "US7833417",
            "US7625485", "US7794596", "US7879245", "US7625489", "US7892432",
        ],
        'negative': [
            "US8038875", "US7794590", "US8017001", "US7901606", "US8038638",
            "US7429329", "US7485259", "US7713416", "US7632409", "US7454295",
            "US7678266", "US8039206", "US7384564", "US7485225", "US7419593",
            "US7374655", "US8075766", "US7727940", "US7368057", "US7799233",
            "US7703285", "US7727392", "US8075776", "US7449114", "US7595000",
        ]
    },
]


def learn(compound_index):
    # We try to fit a function: `y = w1.x1 + w2.x2 ... wn.xn`
    # Where y values for known positive docs = 10 and y values for known
    # negative docs = 0.
    negative_score_bound = 0
    positive_score_bound = 10

    # Optimise using first dataset.
    for data in TRAINING_DATA:
        query_xml = data['query_xml'].strip()
        s = search.Search(query_xml, compound_index)
        # Override all weights to be 1.
        s.override_features_weights([1] * len(search.Search.FEATURES))
        results = s.execute(verbose=True)

        y = []
        x = []
        for result in results:
            if result[-1] in data['positive']:
                y.append(positive_score_bound)

            if result[-1] in data['negative']:
                y.append(negative_score_bound)

            x.append(result[1])

        data['y'] = y
        data['x'] = x

    def f(weights, dataset=0):
        """Returns the root mean squared deviation from the positive/negative
        bounds specified above.

        """
        x = TRAINING_DATA[dataset]['x']
        y = TRAINING_DATA[dataset]['y']

        total_deviation = 0
        for idx, desired_score in enumerate(y):
            predictor_values = x[idx]
            score = utils.dot_product(weights, predictor_values)

            if desired_score == positive_score_bound:
                deviation = desired_score - min(desired_score, score)
            else:
                deviation = max(desired_score, score) - desired_score

            total_deviation += deviation**2

        return float(total_deviation) / len(y)

    print '# Root mean squared with current weights'
    print 'Dataset 0:', f(s.old_features_weights, dataset=0)
    print 'Dataset 1', f(s.old_features_weights, dataset=1)

    print '# Root mean squared with new weights (fmin_powell)'
    result = scipy.optimize.fmin_powell(f, [1] * len(search.Search.FEATURES))
    print result
    print 'Dataset 0', f(result, dataset=0)
    print 'Dataset 1', f(result, dataset=1)

    print '# Root mean squared with new weights (downhill simplex)'
    result = scipy.optimize.fmin(f, [1] * len(search.Search.FEATURES))
    print result
    print 'Dataset 0', f(result, dataset=0)
    print 'Dataset 1', f(result, dataset=1)

    print '# Root mean squared with new weights (BFGS)'
    result = scipy.optimize.fmin_bfgs(f, [1] * len(search.Search.FEATURES))
    print result
    print 'Dataset 0', f(result, dataset=0)
    print 'Dataset 1', f(result, dataset=1)


def evaluate(weights=None):
    for data in TRAINING_DATA:
        query_xml = data['query_xml'].strip()
        s = search.Search(query_xml, compound_index)
        if weights:
            s.override_features_weights(weights)
        results = s.execute(verbose=True)

        for result in results:
            if result[-1] in data['positive']:
                y.append(positive_score_bound)

            if result[-1] in data['negative']:
                y.append(negative_score_bound)



def main(args):
    dictionary_file = os.path.abspath(args.dictionary)
    compound_index = compoundindex.CompoundIndex(dictionary_file)
    learn(compound_index)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Patsnap assignment - Learn')
    parser.add_argument('-d', '--dictionary', help='dictionary file.',
        default='run/dictionary.txt')
    args = parser.parse_args()
    main(args)
