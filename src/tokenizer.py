from nltk import pos_tag, word_tokenize, sent_tokenize
from nltk.stem.snowball import SnowballStemmer


# Initialise the stemmer exactly once to remove overheads when running
# multiple times.
__stemmer = SnowballStemmer('english')


def stem_all(words):
    return [__stemmer.stem(w) for w in words]


# This is the tokeniser from homework 3.
# Uses sent_tokenize(), case-folds, word_tokenize(), then stems using Porter
# Stemmer.
def free_text(text):
    global __stemmer
    try:
        sentences = sent_tokenize(text)
        words = []
        for sent in sentences:
            sent = sent.lower()
            words += word_tokenize(sent.strip())
        words = stem_all(words)
        return words
    except TypeError:
        print u'TypeError while processing text: {}\nNo tokens were returned' \
              .format(text)
        return []
