import json
import os

THESAURUS_PATH = '../run/thesaurus.json'

class Thesaurus(object):
    def __init__(self, thesaurus_path=THESAURUS_PATH):
        thesaurus = os.path.abspath(os.path.join(os.path.dirname(__file__), thesaurus_path))
        with open(thesaurus, 'r') as f:
            self.__backing = json.load(f)

    def __getitem__(self, index):
        if not index:
            return []
        if type(index) is not str:
            raise TypeError('Key must be type(str)')
        return self.__backing.get(index, [])
