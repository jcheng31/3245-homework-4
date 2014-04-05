from ordered_dict import OrderedDict
from nose.tools import eq_ as assert_eq


def test_ordered_dict_set_item():
    o = OrderedDict()
    o['a'] = 1
    o['b'] = 'asdf'

    assert_eq(1, o['a'])
    assert_eq('asdf', o['b'])

    try:
        o['c']
        assert False, 'Should throw key error'
    except KeyError:
        pass


def test_ordered_dict_get_item():
    o = OrderedDict()
    o['a'] = 1
    o['b'] = 'asdf'

    assert_eq(1, o['a'])
    assert_eq(1, o.get('a'))
    assert_eq('asdf', o['b'])
    assert_eq('asdf', o.get('b'))
    assert_eq(None, o.get('c'))


def test_ordered_dict_del_item():
    o = OrderedDict()
    o['a'] = 1
    o['b'] = 'asdf'

    assert_eq(1, o['a'])
    assert_eq('asdf', o['b'])

    del o['a']
    assert_eq(None, o.get('a'))
    try:
        o['a']
        assert False, 'Should throw key error'
    except KeyError:
        pass


def test_ordered_dict_len():
    o = OrderedDict()
    o['a'] = 1
    o['b'] = 'asdf'

    assert_eq(1, o['a'])
    assert_eq('asdf', o['b'])
    assert_eq(2, len(o))

    del o['a']
    assert_eq(1, len(o))

    o['c'] = 'qwer'
    assert_eq(2, len(o))

    del o['c']
    del o['b']
    assert_eq(0, len(o))


def test_ordered_dict_contains():
    o = OrderedDict()
    o['a'] = 1
    o['b'] = 'asdf'

    assert 'a' in o
    assert 'b' in o
    assert 'c' not in o

    del o['a']
    assert 'a' not in o

    o['c'] = 2
    assert 'c' in o


def test_ordered_dict_popitem():
    o = OrderedDict()
    o['a'] = 1
    o['b'] = 'asdf'

    assert_eq(1, o.popitem(True))
    assert_eq(1, len(o))

    o['a'] = 1
    assert_eq(1, o.popitem())
    assert_eq(1, len(o))
