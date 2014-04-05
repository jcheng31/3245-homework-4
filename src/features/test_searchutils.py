import math

from searchutils import *
from nose.tools import eq_ as assert_eq
from nose.tools import raises

def test_unit_vector_single():
    vector = (1,)
    assert_eq((1,), tuple(unit_vector(vector)))

    vector = (2,)
    assert_eq((1,), tuple(unit_vector(vector)))

    vector = (10,)
    assert_eq((1,), tuple(unit_vector(vector)))

def test_unit_vector_multiple():
    vector = (1, 2)
    length = math.sqrt(1**2 + 2**2)
    assert_eq(
        (float(1)/length, float(2)/length),
        tuple(unit_vector(vector)))

    vector = (3, 5)
    length = math.sqrt(3**2 + 5**2)
    assert_eq(
        (float(3)/length, float(5)/length),
        tuple(unit_vector(vector)))

@raises(TypeError)
def test_unit_vector_generator():
    vals = [0,1,2,3,4]
    vector = (x for x in vals)
    length = math.sqrt(1 + 4 + 9 + 16)
    assert_eq(
        (float(0)/length, float(1)/length, float(2)/length, float(3)/length,
            float(4)/length),
        tuple(unit_vector(vector)))


def test_dot_product():
    v1 = (1,)
    v2 = (2,)
    assert_eq(1 * 2, dot_product(v1, v2))

    v1 = (1, 1)
    v2 = (2, 2)
    assert_eq(
        1 * 2 + 1 * 2,
        dot_product(v1, v2))

    v1 = (3, 6)
    v2 = (2, 5)
    assert_eq(
        3 * 2 + 6 * 5,
        dot_product(v1, v2))

def test_dot_product_generators():
    vals = [0,1,2,3,4]
    v1 = (x for x in vals)
    v2 = (x for x in vals)
    assert_eq(
        1 + 4 + 9 + 16,
        dot_product(v1, v2))
