from nltk import word_tokenize, sent_tokenize
from nltk.stem.porter import PorterStemmer


__stemmer = PorterStemmer()


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
        return [__stemmer.stem(w) for w in words]
    except TypeError:
        print 'TypeError while processing text: {}\nNo tokens were returned' \
              .format(text)
        return []
