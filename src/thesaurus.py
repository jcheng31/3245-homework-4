import json
from os.path import abspath, join, dirname


THESAURUS_PATH = 'thesaurus.json'


class Thesaurus(object):
    """
    The Thesaurus object is a thin wrapper around a Python dictionary type.
    """
    def __init__(self, thesaurus_path=THESAURUS_PATH):
        thesaurus = abspath(join(dirname(__file__), thesaurus_path))
        with open(thesaurus, 'r') as f:
            self.__backing = json.load(f)

    def __getitem__(self, index):
        """
        Retrieves a word from the thesaurus.

        If the word is None, or does not exist in the thesaurus, returns an
        empty list.
        """
        if not index:
            return []
        if type(index) is not str:
            raise TypeError('Key must be type(str)')
        return self.__backing.get(index, [])
