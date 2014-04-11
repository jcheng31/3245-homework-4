import patentfields

from features.vsm import single
from thesaurus import Thesaurus
from helpers import cache
from tokenizer import free_text as tokenizer


class VSMSingleFieldMinusStopwordsPlusExpansion(
        single.VSMSingleFieldMinusStopwords):
    def stemmed_unstemmed_map(self, index):
        # TODO(michael): Cache this value.
        stemmed_unstemmed_dict = {}
        stems = self.search.get_tokens_for(index)
        originals = self.search.get_tokens_for(index, unstemmed=True)

        for idx, stem in enumerate(stems):
            stemmed_unstemmed_dict[stem] = originals[idx]

        return stemmed_unstemmed_dict

    def matches(self, term):
        # Obtain the postings list for this term.
        term_postings = \
            set(self.compound_index.postings_list(self.INDEX, term))

        # Find synonyms of the term from our thesaurus.
        thesaurus = Thesaurus()
        unstemmed = self.stemmed_unstemmed_map(self.INDEX)[term]
        synonyms = thesaurus[unstemmed]

        # Add each synonym's postings to the main posting list.
        for synonym in synonyms:
            stemmed_synonym = tokenizer(synonym)[0]
            postings = self.compound_index.postings_list(
                self.INDEX, stemmed_synonym)
            term_postings = term_postings.union(postings)

        return sorted(term_postings)


class VSMTitleMinusStopwordsPlusExpansion(
        VSMSingleFieldMinusStopwordsPlusExpansion):
    NAME = 'VSM_Title_Minus_Stopwords_Plus_Expansion'
    INDEX = patentfields.TITLE


class VSMAbstractMinusStopwordsPlusExpansion(
        VSMSingleFieldMinusStopwordsPlusExpansion):
    NAME = 'VSM_Abstract_Minus_Stopwords_Plus_Expansion'
    INDEX = patentfields.ABSTRACT
