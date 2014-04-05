class OrderedDict(object):
    def __init__(self):
        self._innerdict = {}
        self._keys = []

    def __getitem__(self, key):
        return self._innerdict[key]

    def get(self, key):
        return self._innerdict.get(key)

    def __setitem__(self, key, item):
        self.maybe_add_key(key)
        self._innerdict[key] = item

    def maybe_add_key(self, key):
        if key not in self._innerdict:
            self._keys.append(key)

    def maybe_remove_key(self, key):
        if key in self._keys:
            self._keys.remove(key)

    def __delitem__(self, key):
        self.maybe_remove_key(key)
        del self._innerdict[key]

    def __contains__(self, key):
        return key in self._innerdict

    def __len__(self):
        return len(self._innerdict)

    def __str__(self):
        return '%s.%s' % (self.__class__.__name__, self._innerdict)

    def __repr__(self):
        return str(self)

    def popitem(self, fifo=False):
        idx = 0 if fifo else -1
        key = self._keys[idx]
        val = self[key]
        del self[key]
        return val
