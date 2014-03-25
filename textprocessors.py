import patentfields
from nltk import word_tokenize, sent_tokenize
from nltk.stem.porter import PorterStemmer


__stemmer = PorterStemmer()


# This is the tokeniser from homework 3.
# Uses sent_tokenize(), case-folds, word_tokenize(), then stems using Porter
# Stemmer.
def hw3_tokenizer(text):
    global __stemmer
    sentences = sent_tokenize(text)
    words = []
    for sent in sentences:
        sent = sent.lower()
        words += word_tokenize(sent.strip())
    return [__stemmer.stem(w) for w in words]

# To add new fields to the index, or to modify the tokenisation behavior of
# a field, write a new tokenising function, and add it to extract_fields
# below.
# All tokenizers must return a list of strings that represent tokens to be
# added to the dictionary file.
__title_tokenizer = hw3_tokenizer
__abstract_tokenizer = hw3_tokenizer
extract_fields = {
    patentfields.TITLE: __title_tokenizer,
    patentfields.ABSTRACT: __abstract_tokenizer
}
