import utils
import compoundindex
import json


def search(dictionary_file, postings_file, query_file, output_file):
    print dictionary_file
    print postings_file
    print query_file
    print output_file

    compound_index = compoundindex.CompoundIndex(dictionary_file)
    query = utils.parse_query_file(query_file)
