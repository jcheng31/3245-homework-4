import utils
import json


def search(dictionary_file, postings_file, query_file, output_file):
    print dictionary_file
    print postings_file
    print query_file
    print output_file

    # Read and build index files
    with open(dictionary_file, 'r') as dfile:
        dictionary = json.loads(dfile.read())

    # Read and parse query_file
    query = utils.parse_query_file(query_file)
