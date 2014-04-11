This is the README file for A0092104U, A0082877M, and A0080860H's submission.
Matric Numbers: A0092104U, A0082877M, A0080860H
Emails: a0092104@nus.edu.sg, a0082877@nus.edu.sg, a0080860@nus.edu.sg

== General Notes about this assignment ==

# Index
The indexer iterates through the directory of patents and performs tokenization
and stemming on parts of each patent document.

We consider two types of fields in each XML document.

    “Zones” are XML fields that contain free text. Text in these fields are
    tokenized and stemmed before being added to the dictionary.

    “Fields” are XML fields that contain structured data. Text in these fields
    are added directly to the dictionary without being tokenized or stemmed.

This implementation does not separate the index and postings list into two
files. The filename passed as a command line argument is ignored. We decided on
such an approach when initial experiments showed that the file size of the
combined index-postings was about 3.5MiB -- small enough to be entirely memory
resident.

During indexing, we continuously add terms, postings, and fields to a Python
dictionary. When all documents have been processed, this dictionary is
serialised to a JSON file. The Python class CompoundIndex exposes an abstract
interface through which the generated dictionary may be queried. In the process
of serialization, integer types that we use as keys are converted to strings.
These strings are re-parsed into integers when the dictionary is loaded in
search.py.

In the indexing phase, we assume that all patent documents are well formed. If
any operation on a patent document causes a processing error, the entire
document is discarded. Additionally, only files with the “.xml” extension are
processed. Possible documents in all other formats are ignored.

# Search

At a high level, the search is basically comprised of features. Given a query,
each feature assigns a document a score. The main search object calculates the
feature scores for each document and aggregates these scores into a feature
score vector.

We also maintain a list of “weights” that correspond to how the features scores
correlate to relevance. (Changing the weights of various features will change
the results of our search, Notice that the weights of particular features can
therefore be tweaked independently of other features to tune the search system
based on feedback/training.).

After calculating the feature scores for each feature. We get a mapping of
doc_ids to feature score vector.

        doc1 => (s1, s2, ... sn),
        doc2 => (s1, s2, ... sn),
        …

Each of these features could be a simple vsm done on a single index, or a score
based on how many citations the document has.

We then do a dot product of these scores against a tuple of various predefined
thresholds to arrive at a final absolute score for each document.

Based on these scores, the documents are sorted and returned in order. (We
optionally have a min score that defines a minimum score that a document has to
hit in order to qualify as 'relevant').

# Features

## VSM
The general idea is to use a vector space model (VSM) to score documents.

We extend this base class in several ways to provide several different VSM
scores (which operate on different indices etc.). Each subclass overrides (among
other methods) `query_tokens` and `matches` to specify the query and field for
the VSM.

At a high-level, each VSM feature has a query (returned by `query_tokens`):
    [A, B, C]

and a call to matches (with a term) should return a postings list:
    self.matches(A) => [(d1, tf), (d2, tf) ... ]

Through a simple class hierarchy, we are able to create VSM features for:
    - Title
    - Abstract
    - Title Minus Stopwords
    - Abstract Minus Stopwords
    - Title Nouns only
    - Abstract Nouns only
    - Title and Abstract
    - Title and Abstract Minus Stopwords
    - TItle Minus Stopwords Plus Expansion
    - Abstract Minus Stopwords Plus Expansion

## Cluster
The intuition for this feature is that, for the relevant documents, if a
particular field value appears more frequently among the documents that score
well, this is a good signal for relevance.

For each relevant document (so far), we take a rough estimate of the score add it to a bucket (based on that document's value in the specified field.)

We then boost all documents (not only the currently relevant ones) based on which bucket they belong to.

Fields we do clustering:
    - IPC section
    - IPC class
    - IPC group
    - IPC primary
    - IPC subclass
    - IPC all
    - UPC all
    - UPC primary
    - UPC class

## IPC Sections headings
We do a simple expansion of IPC sections to their labels (ie. A => ‘Human
Necessities’ …) and run a simple VSM by treating the the resulting text as a
free text zone.

## Relation
Some fields in patents references other patents. The intuition is that, for the
relevant documents, if they are related to other documents (cite them, are
family members etc), this is a good signal for relevance.

We do this for the following fields:
	- Citations
	- Family Members

## Fields
Field-based features simply score documents based on the value of a particular
field. For eg, we have a ‘Cites’ feature that assigns a score based on the
number of citations a document has.

# Query Expansion
Query expansion is done as a variant of the normal VSM method, and is handled
separately for title and abstract. The basic idea in our implementation is to
treat synonyms of a word as if they were the word itself: we simply add to their
term frequency counts.

We obtained synonyms from the AlterVista thesaurus API (linked in references) by
calling it with a list of all nouns and adjectives found in the PatSnap corpus.
This was done as a pre-processing step, and is not carried out during
run/query-time.

# Field/Zone treatment
In the indexing phase we index fields and zones differently (As above):
    “Zones” are XML fields that contain free text. Text in these fields are
    tokenized and stemmed before being added to the dictionary.

    “Fields” are XML fields that contain structured data. Text in these fields
    are added directly to the dictionary without being tokenized or stemmed.

During search, the fields and zones are dealt with multiple features. For zones,
most of the features are VSM basd. While for fields, they mainly take the form
of clusters/relation and field based features, elaborated above.

# Learning
This part involves figuring out what weights to use for our features. We use
`scipy.optimize` to reduce the “error” of our search system by minimizing the
return value of `1 - F` across our training dataset.

# Allocation of work
A0082877M: Basic structure of Search, Implemented some features, Implemented learn.py
A0092104U: Index (File System), Thesaurus, File Format, Makefile, Process Automation, Came up with team name,.
A0080860H: Index (XML to Dictionary), Search (Query Expansion)

== Files included with this submission ==
README.txt - this text file.
index.py - Main Index class/entry point to indexing.
search.py - Main search class/entry point to search.
features/ - Contains code of the various features implemented
	__init__.py
	cluster.py - Contains Cluster based features.
	fields.py - Contains Field-based features
	ipc.py - Contains IPC based features
	relation.py - Contains Relation based features
	vsm/ - Contains code for the VSM feature (which the is most complex set of features, hence its own subfolder)
		__init__.py
		base.py - Provides the base class used for all Vector Space Model (VSM) features.
		expansion.py - Handles VSM for a single field (minus stopwords), with query expansion through synonyms.
		multiple.py  - Handles VSM for multiple fields combined, with and without stopwords.
		single.py - Handles VSM for a single field, with and without stopwords.
		test_vsmutils.py - Unit tests for VSM helper methods.
		vsmutils.py - Helper methods (normalising vectors, calculating log-tf, and idf) used for VSM.
helpers/ - Helper methods
	__init__.py
	cache.py - This file contains basic cache decorators.
	ordered_dict.py - Polyfill for collections.OrderedDict (Present in 2.7 but not 2.6)
	test_cache.py - Test file for cache.py
	test_ordered_dict.py - Test file for ordered_dict.py
indexfields.py - File containing string constants used as dictionary keys in our CompoundIndex
learn.py - File with code to train features and determine the optimal coefficients to use.
patentfields.py - File containing string constants of keys in the XML documents
compoundindex.py - Class exposing methods to access postings lists and other fields of indexed documents
thesaurus.json - A thesaurus downloaded from AlterVista. The structure of the thesaurus is { ‘word’: [‘synonyms’, …], ... }
thesaurus.py - A thin wrapper around thesaurus.json.
thesaurus_builder.py - Standalone Python script that downloads a thesaurus from an endpoint.
tokenizer.py - File containing helper functions used to tokenize free text
utils.py - Utility methods used everywhere (xml to dict, dot_product, etc..)


== Adherence to Class Guidelines ==

[X] We, A0092104U, A0082877M, and A0080860H, certify that we have followed the
CS 3245 Information Retrieval class guidelines for homework assignments.
In particular, we expressly vow that we have followed the Facebook rule in
discussing with others in doing the assignment and did not take notes
(digital or printed) from the discussions.

[ ] We, A0092104U, A0082877M, and A0080860H, did not follow the class rules
regarding homework assignment, because of the following reason:

N/A

We suggest that we should be graded as follows:

N/A

== References ==
Apart from the NLTK and Python documentation, we made use of the following
resources:


