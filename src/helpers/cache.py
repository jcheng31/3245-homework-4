try:
    from collections import OrderedDict
except ImportError:
    # Python 2.6 and lower
    from ordered_dict import OrderedDict


def generic_func_cache_key(*args, **kwargs):
    """Cache key generator that simply concaternates all the arguments to the
    function.

    This is the default cache key generator.
    """
    return '%s:%s' % (args, kwargs)


def single_arg_cache_key(*args, **kwargs):
    """Cache key generator that only takes into consideration the first
    argument.
    """
    return '%s' % args[0]


class CacheBox(object):
    """A simple cache wrapper for a function.

    Exploits the callable behavior of clases to provide basic cache handling
    methods. (Checking if value is cached, Invalidating existings values etc.)

    Takes in the function to cache as well a optional cache_key_func which is
    used to generate the key used to cached the computed values.
    """
    def __init__(self, func, cache_key_func=None):
        self.func = func
        self._cache = {}
        self.cache_key_func = cache_key_func or generic_func_cache_key

    def __call__(self, *args, **kwargs):
        """Behavior similar to calling the cached function."""
        return self.hard_get(*args, **kwargs)

    def cache_key(self, *args, **kwargs):
        """Computes and returns the cache key."""
        return self.cache_key_func(*args, **kwargs)

    def is_cached(self, *args, **kwargs):
        """Returns a boolean indicating if a value has been cached."""
        return self.cache_key(*args, **kwargs) in self._cache

    def invalidate(self, *args, **kwargs):
        """Removes a cached value from the cache."""
        cache_key = self.cache_key(*args, **kwargs)
        self._cache.pop(cache_key, None)

    def hard_get(self, *args, **kwargs):
        """Returns value either from cache if exists or directly invoking the
        wrapped function.

        Caches value before returning.
        """
        cache_key = self.cache_key(*args, **kwargs)
        if cache_key in self._cache:
            return self._cache[cache_key]

        val = self.func(*args, **kwargs)
        self._cache[cache_key] = val
        return val


class LRUCacheBox(CacheBox):
    """LRU version of the cachebox.

    Defaults to maximum of 1000 keys.

    """
    def __init__(self, func, cache_key_func=None, cache_size=1000):
        super(LRUCacheBox, self).__init__(func, cache_key_func)
        self._cache = OrderedDict()
        self.cache_size = cache_size

    def current_size(self):
        return len(self._cache)

    def check_size(self):
        # http://stackoverflow.com/questions/2437617/ \
        # limiting-the-size-of-a-python-dictionary
        while self.current_size() > self.cache_size:
            self._cache.popitem(False)

    def hard_get(self, *args, **kwargs):
        val = super(LRUCacheBox, self).hard_get(*args, **kwargs)
        self.check_size()
        return val


def cached_function(cache_key_func=None, cache_size=None):
    """Decorator used to turn a function into a cachebox."""
    def cache_decorator(func):
        if cache_size is None:
            return CacheBox(func, cache_key_func=cache_key_func)
        else:
            return LRUCacheBox(
                func,
                cache_key_func=cache_key_func,
                cache_size=cache_size)
    return cache_decorator


def naive_class_method_cache(func):
    """Naive decorator to cache methods."""
    __cache = {}
    def cache_key(*args, **kwargs):
        return "%s:%s:%s" % (func.__name__, args[0][1:], kwargs)

    def new_func(*args, **kwargs):
        key = cache_key(args, kwargs)
        if key in __cache:
            return __cache[key]

        val = func(*args, **kwargs)
        __cache[key] = val
        return val

    def invalidate(*args, **kwargs):
        key = cache_key(args, kwargs)
        __cache.pop(key, None)

    new_func.invalidate = invalidate

    return new_func
