from nltk import pos_tag, word_tokenize, sent_tokenize
from nltk.stem.snowball import SnowballStemmer
# from nltk.stem.porter import PorterStemmer


__stemmer = SnowballStemmer('english')
# __stemmer = PorterStemmer()


# def stem_except_nouns_adjectives(words):
#     pos_words = pos_tag(words)
#     result = []
#     for token, pos in pos_words:
#         if pos in ['NN', 'JJ']:
#             result += token
#         else:
#             result += __stemmer.stem(token)
#     return result


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


