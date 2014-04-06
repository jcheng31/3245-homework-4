import xml.etree.ElementTree as ElementTree

from itertools import izip
from nltk.corpus import stopwords


def xml_file_to_dict(file_path):
    """
    Given the path to a file containing a patent
    in XML form, returns a dictionary representing
    the patent within that file.
    """
    xml_tree = ElementTree.parse(file_path)
    root = xml_tree.getroot()

    dict_representation = root_node_to_dictionary(root)
    return dict_representation


def root_node_to_dictionary(root):
    dict_representation = {}

    for element in root:
        key = element.attrib['name']
        value = element.text.strip() if element.text else None

        if not value:
            # Normalise null or empty values to empty string.
            value = ''

        dict_representation[key] = value

    return dict_representation


def parse_query_xml(xml):
    """Returns a dictionary representation of the query xml."""
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


def without_stopwords(word_lst):
    """Given a list of strings, returns a list without stopwords."""
    stop = stopwords.words('english')
    return [word for word in word_lst if word not in stop]
