import math
import utils

from types import GeneratorType

LOG_BASE = 10

dot_product = utils.dot_product


def unit_vector(vector):
    """Calculates the unit vector to the given vector.

    Expects vector as an iterable. Returns a generator.
    """
    # NOTE(michael): We raise a warning here for generators because we need to
    # loop over all the elements twice (once for the length and once for the
    # actual construction of the unit vector). Since, generators can only be
    # used once, you probably want to pass in a list instead.
    if isinstance(vector, GeneratorType):
        raise TypeError("Use a list/tuple instead.")

    length = math.sqrt(sum(x ** 2 for x in vector))
    if length == 0:
        return (0 for x in vector)
    return (float(x)/length for x in vector)


def logtf(term_frequency):
    """Calculates the logtf given the tf of a term."""
    if term_frequency == 0:
        return 0
    return 1 + math.log(term_frequency, LOG_BASE)


def idf(n, df):
    """Calculates idf given n and df.

    n: number of documents
    df: document frequency of term
    """
    if df == 0 or n == 0:
        return 0
    return math.log(float(n) / df, LOG_BASE)


def stemmed_tokens(query_tokens):
    """Returns a list of stems from a list of tuples of query tokens."""
    return [x.stem for x in query_tokens]
