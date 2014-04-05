from cache import *
from nose.tools import eq_ as assert_eq


def test_cache_box_simple():
    x = {}
    x['val'] = 0

    def test_func():
        x['val'] += 1
        return x['val']

    cached_test_func = CacheBox(test_func)

    assert_eq(0, x['val'])
    assert_eq(1, cached_test_func())

    # Value does not change.
    assert_eq(1, cached_test_func())
    assert_eq(1, x['val'])
    assert_eq(1, cached_test_func())
    assert_eq(1, x['val'])


def test_cache_box_is_cached():
    def test_func(x):
        return x

    cached_test_func = CacheBox(test_func)
    assert not cached_test_func.is_cached(5)

    assert_eq(5, cached_test_func(5))
    assert cached_test_func.is_cached(5)

    assert not cached_test_func.is_cached(4)


def test_cache_box_invalidate():
    def test_func(x):
        return x

    cached_test_func = CacheBox(test_func)
    assert not cached_test_func.is_cached(5)

    assert_eq(5, cached_test_func(5))
    assert cached_test_func.is_cached(5)

    cached_test_func.invalidate(5)
    assert not cached_test_func.is_cached(5)

    assert_eq(5, cached_test_func(5))
    assert cached_test_func.is_cached(5)


def test_lru_cache_box():
    def test_func(x):
        return x

    lru_cached_test_func = LRUCacheBox(test_func, cache_size=10)
    assert_eq(0, lru_cached_test_func.current_size())

    lru_cached_test_func(1)
    assert_eq(1, lru_cached_test_func.current_size())

    lru_cached_test_func.invalidate(1)
    assert_eq(0, lru_cached_test_func.current_size())

    for i in xrange(50):
        lru_cached_test_func(i)

    assert_eq(10, lru_cached_test_func.current_size())


def test_naive_class_method_cache():
    x = {}
    x['val'] = 0

    class Test(object):
        @naive_class_method_cache
        def blah(self):
            x['val'] += 1

    t = Test()

    assert_eq(0, x['val'])
    t.blah()
    assert_eq(1, x['val'])
    t.blah()
    assert_eq(1, x['val'])

    # Invalidate
    t.blah.invalidate()
    t.blah()
    assert_eq(2, x['val'])
