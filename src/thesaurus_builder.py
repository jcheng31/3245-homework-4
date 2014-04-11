#!/usr/env/python
import argparse
import json
import os
import patentfields
import requests
import utils

from nltk import pos_tag, word_tokenize, sent_tokenize

# Note:
# This file is used to download an offline copy of a thesaurus, stored as a
# JSON dictionary. It should not be run unless a new API endpoint is used.


def tokenize(text):
    """
    Tokenizes a string using sent_tokenize and word_tokenize.

    Does not stem individual words.
    """
    words = []
    sentences = sent_tokenize(text)
    for sent in sentences:
        sent = sent.lower()
        words += word_tokenize(sent)
    return words


def extract_nouns_and_adjectives(words):
    """
    For a given list of pos-tagged words, removes words with tags that are
    not in a whitelist.

    Mnemonics for other parts of speech can be found at the following URL:
    http://www.monlp.com/2011/11/08/part-of-speech-tags/
    """
    pos_words = pos_tag(words)
    nouns = set()
    for token, pos in pos_words:
        if pos in ['NN', 'JJ']:
            nouns.add(token)
    return list(nouns)


# The Watson Thesaurus was not comprehensive enough for our use case.

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
    """
    Source: See ENDPOINT.
    """
    ENDPOINT = 'http://thesaurus.altervista.org/thesaurus/v1?word={term}&' + \
               'language=en_US&key={key}&output=json'

    # This key will be revoked after the course. It is not required as a local
    # copy of the downloaded thesaurus is already provided in `thesaurus.json`.
    API_KEY = 'PAkqMalR6aTH3rTcndnT'

    @staticmethod
    def build_thesaurus(words, outfile, limit=None):
        """
        Given a list of words, queries the API and builds a local copy of the
        thesaurus, stored as a JSON file at outfile.

        The parameter limit can be used to debug the implementation by
        specifying the number of words to be downloaded.

        Some APIs may temporarily ban an IP address that makes too many
        requests in a short span of time. This implementation does not provide
        rate limiting functionality as this particular endpoint is not rate
        limited.
        """
        thesaurus = {}

        # Keep count of words processed so far as a progress meter.
        print 'Words: {}'.format(len(words))
        count = 0

        for w in words:
            try:
                # Update progress meter.
                count += 1
                if count % 10 == 0:
                    print 'Processed: {} of {}'.format(count, len(words))

                # Make request to endpoint.
                url = AltervistaThesaurus.ENDPOINT.format(
                    term=w, key=AltervistaThesaurus.API_KEY)
                response = requests.get(url)
                json_obj = response.json()
                synonyms = AltervistaThesaurus.__parse_response(json_obj)
            except Exception:
                synonyms = []
                print 'Exception in: ', w

            # Assign list of synonyms to the corresponding word, or an empty
            # list.
            thesaurus[w] = synonyms

            # Debug instrumentation.
            if limit and count >= limit:
                break

        print 'Writing file...'
        with open(outfile, 'w') as f:
            json.dump(thesaurus, f)
        print 'Done!'

    @staticmethod
    def __parse_response(json_obj):
        """
        Parses the JSON object that the API returns.
        """
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
    """
    Processes all XML files in a given directory.

    The fields from each XML file that should be extracted must be specified
    in the class parameter ZONES.
    """
    ZONES = [
        patentfields.TITLE,
        patentfields.ABSTRACT,
    ]

    def __init__(self, doc_dir, out_file):
        """
        doc_dir: The directory containing the XML documents to process.
        out_file: The file to which the JSON thesaurus will be written.
        """
        # Normalize with trailing slash for consistency.
        if doc_dir[-1] != '/':
            doc_dir += '/'

        self.__doc_dir = doc_dir
        self.__out_file = out_file

    def run(self):
        """
        Begins downloading thesaurus.
        """
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
        nouns = extract_nouns_and_adjectives(unique_words)
        AltervistaThesaurus.build_thesaurus(nouns, self.__out_file)

    def __process_patent(self, doc_id, info):
        """
        Processes a single patent XML.
        """
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
