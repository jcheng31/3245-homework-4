import json
import requests
from os.path import isfile


class BingSynonyms(object):
    def __init__(self, user, api_key, cache_file):
        self.user = user
        self.api_key = api_key

        self.cache = dict()
        try:
            if isfile(cache_file):
                with open(cache_file, 'r') as f:
                    self.cache = json.load(f)
        except ValueError:
            pass
        except IOError:
            pass

        self.cache_file = cache_file

    def get(self, word):
        if word in self.cache:
            return self.cache[word]

        endpoint = 'https://{user}:{key}@api.datamarket.azure.com/Bing/' +\
                   'Synonyms/v1/GetSynonyms?Query=%27{word}%27&$format=JSON'
        token = word.translate(None, '\'\"')
        uri = endpoint.format(user=self.user, key=self.api_key,
                              word=token)
        response = requests.get(uri).json()
        synonyms = [r['Synonym'] for r in response['d']['results']]

        self.cache[word] = synonyms
        self.__serialize()
        return synonyms

    def __serialize(self):
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f)
        except IOError:
            pass
