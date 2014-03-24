import xml.etree.ElementTree as ElementTree

class Patent(object):
    """Class used to parse an entire Patent with all its fields."""

    @staticmethod
    def from_file(file_path):
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
        key = element.attrib["name"]
        value = element.text.strip() if element.text else None

        if value:
            # Handle lists, which are delimited in the XML by |
            split = value.split("|")
            value = map(str.strip, split) if len(split) > 1 else value

        dict_representation[key] = value

    return dict_representation