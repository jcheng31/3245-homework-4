import xml.etree.ElementTree as ElementTree

from itertools import izip
from nltk.corpus import stopwords
from nltk.corpus import wordnet


def xml_file_to_dict(file_path):
    """
    Given the path to a file containing a patent
    in XML form, returns a dictionary representing
    the patent within that file.
    """
    # We use ElementTree to load the XML file
    # and handle actual parsing.
    xml_tree = ElementTree.parse(file_path)
    root = xml_tree.getroot()

    # Pass off to our helper to do actual conversion into
    # a dictionary.
    dict_representation = root_node_to_dictionary(root)
    return dict_representation


def root_node_to_dictionary(root):
    """Given the root node of an ElementTree, returns
    a dictionary where keys are the 'name' attributes
    of each XML node contained within, and values are
    the text contained within that node."""
    dict_representation = {}

    for element in root:
        key = element.attrib['name']
        value = element.text.strip() if element.text else None

        if not value:
            # Normalise null or empty values to empty string.
            value = ''

        # Normalise to ascii, ignoring unicode.
        value = value.encode('ascii', 'ignore')

        dict_representation[key] = value

    return dict_representation


def parse_query_xml(xml):
    """Given a string of XML representing a query, returns
    a dictionary representing the query."""
    root = ElementTree.fromstring(xml)
    retval = {}
    for child in root:
        retval[child.tag] = child.text.strip()

    return retval


def dot_product(v1, v2):
    """Calculates the dot product of two vectors.

    Expects vectors as an iterable. Returns a number.
    """
    return sum(x * y for x, y in izip(v1, v2))


def without_stopwords(words):
    """Given a list of words, returns a list of words without stopwords."""
    stop = stopwords.words('english')
    return [word for word in words if word not in stop]


def synonyms(word):
    """Given a word, returns a list of synonyms from WordNet."""
    synsets = wordnet.synsets(word)
    all_synonyms = [lemma.name for syn in synsets for lemma in syn.lemmas]
    unique_synonyms = set(all_synonyms)
    return sorted(list(unique_synonyms))
