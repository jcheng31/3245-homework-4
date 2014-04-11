import base
import patentfields
import utils

from nltk import pos_tag


class VSMSingleField(base.VSMBase):
    """VSM feature using a single index.

    This looks at the stemmed tokens within a single component of the query.
    """
    INDEX = None

    def idf(self, term):
        return self.compound_index.inverse_document_frequency(
            self.INDEX, term)

    def query_tokens(self):
        return self.search.get_tokens_for(self.INDEX)

    def matches(self, term):
        return self.compound_index.postings_list(self.INDEX, term)


class VSMTitle(VSMSingleField):
    NAME = 'VSM_Title'
    INDEX = patentfields.TITLE


class VSMAbstract(VSMSingleField):
    NAME = 'VSM_Abstract'
    INDEX = patentfields.ABSTRACT


class VSMSingleFieldMinusStopwords(VSMSingleField):
    """VSM feature using a single field, removing stopwords."""
    def query_tokens(self):
        query_tokens = super(VSMSingleFieldMinusStopwords,
            self).query_tokens()
        return utils.without_stopwords(query_tokens)


class VSMTitleMinusStopwords(VSMSingleFieldMinusStopwords):
    NAME = 'VSM_Title_Minus_Stopwords'
    INDEX = patentfields.TITLE


class VSMAbstractMinusStopwords(VSMSingleFieldMinusStopwords):
    NAME = 'VSM_Abstract_Minus_Stopwords'
    INDEX = patentfields.ABSTRACT


class VSMSingleFieldNounsOnly(VSMSingleField):
    """VSM feature using a single field, considering only nouns."""
    def query_tokens(self):
        query_tokens = super(VSMSingleFieldNounsOnly,
            self).query_tokens()

        # Run the query tokens through a pos tagger and filter out tokens that
        # are not nouns.
        pos_words = pos_tag(query_tokens)
        return [token for token, pos in pos_words if pos == 'NN']

class VSMTitleNounsOnly(VSMSingleFieldNounsOnly):
    NAME = 'VSM_Title_Nouns_Only'
    INDEX = patentfields.TITLE


class VSMAbstractNounsOnly(VSMSingleFieldNounsOnly):
    NAME = 'VSM_Abstract_Nouns_Only'
    INDEX = patentfields.ABSTRACT
