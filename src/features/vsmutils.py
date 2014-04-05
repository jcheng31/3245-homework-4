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
    return (float(x)/length for x in vector)


def logtf(term_frequency):
    if term_frequency == 0:
        return 0
    return 1 + math.log(term_frequency, LOG_BASE)
