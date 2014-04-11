import patentfields

from features.vsm import single
from thesaurus import Thesaurus
from helpers import cache
from tokenizer import free_text as tokenizer


class VSMSingleFieldMinusStopwordsPlusExpansion(
        single.VSMSingleFieldMinusStopwords):
    """Base class for VSM on a single field using synonym expansion of each
    word in the field (ignoring stopwords.)"""

    def stemmed_unstemmed_map(self, index):
        """Given an index, returns a dictionary where keys are stems of the
        words contained within, and values are the corresponding unstemmed
        word."""
        # TODO(michael): Cache this value.
        stemmed_unstemmed_dict = {}
        stems = self.search.get_tokens_for(index)
        originals = self.search.get_tokens_for(index, unstemmed=True)

        for idx, stem in enumerate(stems):
            stemmed_unstemmed_dict[stem] = originals[idx]

        return stemmed_unstemmed_dict

    def matches(self, term):
        """Given a term, returns a list of postings for that term and its
        synonyms.

        We find synonyms for the given term, obtain their postings, and merge
        them with the \"original\" list of postings for the term itself."""
        # Obtain the postings list for this term.
        term_postings = \
            set(self.compound_index.postings_list(self.INDEX, term))

        posting_dict = {}
        for posting in term_postings:
            posting_dict[posting[0]] = posting[1]

        # Find synonyms of the term from our thesaurus.
        thesaurus = Thesaurus()
        unstemmed = self.stemmed_unstemmed_map(self.INDEX)[term]
        synonyms = thesaurus[unstemmed]

        # Add each synonym's postings to the main posting list.
        for synonym in synonyms:
            stemmed_synonym = tokenizer(synonym)[0]
            postings = self.compound_index.postings_list(
                self.INDEX, stemmed_synonym)

            for posting in postings:
                doc_id = posting[0]
                count = posting[1]

                if doc_id in posting_dict:
                    posting_dict[doc_id] += count
                else:
                    posting_dict[doc_id] = count

        combined_postings = []
        for doc_id, count in posting_dict.iteritems():
            combined_postings.append([doc_id, count])

        return sorted(combined_postings)


class VSMTitleMinusStopwordsPlusExpansion(
        VSMSingleFieldMinusStopwordsPlusExpansion):
    NAME = 'VSM_Title_Minus_Stopwords_Plus_Expansion'
    INDEX = patentfields.TITLE


class VSMAbstractMinusStopwordsPlusExpansion(
        VSMSingleFieldMinusStopwordsPlusExpansion):
    NAME = 'VSM_Abstract_Minus_Stopwords_Plus_Expansion'
    INDEX = patentfields.ABSTRACT
