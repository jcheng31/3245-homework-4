import collections
import patentfields

from features import vsm
from tokenizer import free_text


IPC_SECTIONS = {
    'A': free_text('Human Necessities'),
    'B': free_text('Performaing Operations, Transporting'),
    'C': free_text('Chemistry, Metallurgy'),
    'D': free_text('Textiles, Paper'),
    'E': free_text('Fixed Constructions'),
    'F': free_text('Mechanical Engineering, Lighting, Heating, Weapons'),
    'G': free_text('Physics'),
    'H': free_text('Electricity'),
}


class IPCSectionLabels(vsm.VSMSingleFieldMinusStopwords):
    """VSM feature using the text descriptions of the IPC sections."""
    def idf(self, *args, **kwargs):
        return 1

    def matches(self, term, compound_index):
        for section, tokens in IPC_SECTIONS.iteritems():
            if term.stem in tokens:
                retval = []
                for doc_id, val in compound_index.value_for_field(
                        patentfields.IPC_SECTION):
                    if val == section:
                        retval.append((doc_id, 1))
                return retval
        return []


class IPCSectionLabelsTitle(IPCSectionLabels):
    NAME = 'IPC_Section_Labels_Title'
    INDEX = patentfields.TITLE


class IPCSectionLabelsAbstract(IPCSectionLabels):
    NAME = 'IPC_Section_Labels_Abstract'
    INDEX = patentfields.ABSTRACT
