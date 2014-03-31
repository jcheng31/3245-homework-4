import xml.etree.ElementTree as ElementTree


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


def parse_query_file(file_path):
    """Returns a dictionary representation of the query file."""
    with open(file_path, 'r') as f:
        xml = f.read()

    root = ElementTree.fromstring(xml)
    retval = {}
    for child in root:
        retval[child.tag] = child.text.strip()

    return retval
