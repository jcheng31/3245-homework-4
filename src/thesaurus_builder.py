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


# class WatsonThesaurus(object):
#     ENDPOINT = 'http://watson.kmi.open.ac.uk/API/term/synonyms?term={term}'
#     HEADERS = {
#         'Accept': 'application/json'
#     }
#     ARRARR = u'Term-array-array'
#     ARR = u'Term-array'

#     @staticmethod
#     def build_thesaurus(words, outfile):
#         thesaurus = {}
#         print 'Words: {}'.format(len(words))
#         count = 0
#         for w in words:
#             try:
#                 count += 1
#                 if count % 10 == 0:
#                     print 'Processed: {} of {}'.format(count, len(words))
#                 url = WatsonThesaurus.ENDPOINT.format(term=w)
#                 response = requests.get(url, headers=WatsonThesaurus.HEADERS)
#                 json_obj = response.json()

#                 # Parse API response.
#                 trr = json_obj[WatsonThesaurus.ARRARR]
#                 if type(trr) is not dict:
#                     # Word not found in thesaurus API.
#                     continue
#                 trr_trr = trr[WatsonThesaurus.ARR]
#                 if type(trr_trr) is not dict:
#                     # wat...
#                     continue
#                 synonyms = trr_trr[u'Term']
#                 if type(synonyms) is not list:
#                     # No synonyms found.
#                     synonyms = [synonyms]
#             except Exception:
#                 print 'Exception in: ', w

#             thesaurus[w] = synonyms
#         print 'Writing file...'
#         with open(outfile, 'w') as f:
#             json.dump(thesaurus, f)
#         print 'Done!'


class AltervistaThesaurus(object):
    ENDPOINT = 'http://thesaurus.altervista.org/thesaurus/v1?word={term}&' + \
               'language=en_US&key={key}&output=json'
    API_KEY = 'PAkqMalR6aTH3rTcndnT'

    @staticmethod
    def build_thesaurus(words, outfile, limit=None):
        thesaurus = {}
        print 'Words: {}'.format(len(words))
        count = 0
        for w in words:
            try:
                count += 1
                if count % 10 == 0:
                    print 'Processed: {} of {}'.format(count, len(words))
                url = AltervistaThesaurus.ENDPOINT.format(
                    term=w, key=AltervistaThesaurus.API_KEY)
                response = requests.get(url)
                json_obj = response.json()

                synonyms = AltervistaThesaurus.__parse_response(json_obj)
            except Exception:
                synonyms = []
                print 'Exception in: ', w

            thesaurus[w] = synonyms

            if limit and count >= limit:
                break
        print 'Writing file...'
        with open(outfile, 'w') as f:
            json.dump(thesaurus, f)
        print 'Done!'

    @staticmethod
    def __parse_response(json_obj):
        if 'error' in json_obj or 'response' not in json_obj:
            return []
        
        all_synonyms = set()
        forms = json_obj['response']
        for form in forms:
            content = form['list']
            pos = content['category']
            if pos != '(noun)':
                continue

            synonyms_field = content['synonyms']
            synonyms = synonyms_field.split('|')
            for compound_word in synonyms:
                if not compound_word.isalpha():
                    continue

                words = compound_word.split(' ')
                for w in words:
                    all_synonyms.add(w.strip())

        return list(all_synonyms)


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
        AltervistaThesaurus.build_thesaurus(nouns, self.__out_file)

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
