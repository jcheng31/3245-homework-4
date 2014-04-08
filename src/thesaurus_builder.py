import argparse
import json
import os
import patentfields
import requests
import utils

from nltk import pos_tag, word_tokenize, sent_tokenize


def tokenize(text):
    words = []
    sentences = sent_tokenize(text)
    for sent in sentences:
        sent = sent.lower()
        words += word_tokenize(sent)
    return words


def extract_nouns(words):
    pos_words = pos_tag(words)
    nouns = set()
    for token, pos in pos_words:
        if pos == 'NN':
            nouns.add(token)
    return list(nouns)


ENDPOINT = 'http://watson.kmi.open.ac.uk/API/term/synonyms?term={term}'
HEADERS = {
    'Accept': 'application/json'
}
ARRARR = u'Term-array-array'
ARR = u'Term-array'


def build_thesaurus(words, outfile):
    thesaurus = {}
    print 'Words: {}'.format(len(words))
    count = 0
    for w in words:
        print w
        count += 1
        if count % 10 == 0:
            # print 'Processed: {} of {}'.format(count, len(words))
            pass
        url = ENDPOINT.format(term=w)
        response = requests.get(url, headers=HEADERS)
        json_obj = response.json()

        # Parse API response.
        trr = json_obj[ARRARR]
        if type(trr) is not dict:
            # Word not found in thesaurus API.
            continue
        synonyms = trr[ARR][u'Term']
        if type(synonyms) is not list:
            synonyms = [synonyms]

        thesaurus[w] = synonyms
    print 'Writing file...'
    with open(outfile, 'w') as f:
        json.dump(thesaurus, f)
    print 'Done!'


class DirectoryProcessor(object):
    ZONES = [
        patentfields.TITLE,
        patentfields.ABSTRACT,
    ]

    def __init__(self, doc_dir, out_file):
        # Normalize with trailing slash for consistency.
        if doc_dir[-1] != '/':
            doc_dir += '/'

        self.__doc_dir = doc_dir
        self.__out_file = out_file

    def run(self):
        words = []
        for filename in os.listdir(self.__doc_dir):
            doc_id, extension = os.path.splitext(filename)
            if extension.lower() != '.xml':
                print 'Ignoring file: {} Reason: Not an XML document.'\
                      .format(filename)
                continue
            full_path = self.__doc_dir + filename
            patent_info = utils.xml_file_to_dict(full_path)
            words += self.__process_patent(doc_id, patent_info)
        unique_words = list(set(words))
        nouns = extract_nouns(unique_words)
        build_thesaurus(nouns, self.__out_file)

    def __process_patent(self, doc_id, info):
        words = []
        for zone in self.ZONES:
            text = info.get(zone)
            if text:
                words += tokenize(text)
        return words



def main(args):
    args.index = os.path.abspath(args.index)
    args.output = os.path.abspath(args.output)

    dp = DirectoryProcessor(args.index, args.output)
    dp.run()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Patsnap assignment - Index')
    parser.add_argument('-i', '--index', required=True,
                        help='directory of documents.')
    parser.add_argument('-o', '--output', required=True,
                        help='output file.')
    args = parser.parse_args()
    main(args)
