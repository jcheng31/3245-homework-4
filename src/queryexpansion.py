from api.synonyms import BingSynonyms
from nltk import pos_tag
from nltk.stem.porter import PorterStemmer


CACHE_FILE = '/tmp/qxcg_cache.json'
USER = 'cgcai@qxcg.net'
API_KEY = 'y5Uex22ihddkraldyV7CeNDTbwZdMM0NLAJiYMIQDfc='


# TODO(Cam): Abstract into separate file if this gets too big.
# http://www.monlp.com/2011/11/08/part-of-speech-tags/
POS_NOUN = 'NN'


__stemmer = PorterStemmer()
__bing_stemmer = BingSynonyms(USER, API_KEY, CACHE_FILE)


def expand(tokens, processes=[]):
    """
    Applies a set of expansion processes to a list of tokens.
    """
    pos_tokens = pos_tag(tokens)
    expanded = set()
    for pos_t in pos_tokens:
        for proc_func in processes:
            proc_result = proc_func(pos_t)
            for result_item in proc_result:
                expanded.add(result_item)
    return list(expanded)


# Expansion Processes
# Each function should take a (token, part_of_speech)-tuple, perform a single
# expansion, and then return a list of tokens (without parts of speech).
def synonym_expansion(pos_token):
    """
    Returns Bing synonyms, including the original form.
    """
    assert type(pos_token) == tuple
    assert len(pos_token) == 2
    token, pos = pos_token
    result = [token]

    synonyms = __bing_stemmer.get(token)
    for s in synonyms:
        result.append(s)

    return __stem(result)


def __stem(words):
    words = __listify(words)
    stemmed = [__stemmer.stem(w) for w in set(words)]
    return [w for w in stemmed if w]


def __listify(words):
    tokens = []
    for w in words:
        split = w.split(' ')
        for s in split:
            tokens.append(s)
    return tokens
