import json


class Thesaurus(object):
    def __init__(self, thesaurus='../run/thesaurus.json'):
        with open(thesaurus, 'r') as f:
            self.__backing = json.load(f)

    def __getitem__(self, index):
        if type(index) is not str:
            raise TypeError('Key must be type(str)')
        return self.__backing.get(index, [])
