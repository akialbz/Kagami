#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
factor

author(s): Albert (aki) Zhou
origin: 08-08-2018

"""


import sys
import numpy as np
from string import join
from bidict import FrozenOrderedBidict
from kagami.core import NA, hasvalue, optional, checkany, listable, mappable, hashable
from kagami.dtypes import CoreType


# DO NOT call this class directly, use factor()
class _Factor(CoreType):
    __slots__ = ('_array', '_levdct', '_enctype', '_sfmt')

    def __init__(self, labels = NA, array = NA):
        if hasvalue(labels):
            self._array = self.encode(labels)
        elif hasvalue(array):
            self._array = np.array(array, dtype = self._enctype)
            if checkany(np.unique(self._array), lambda x: x not in self._levdct.values()): raise ValueError('array values not recognised')
        else:
            self._array = np.array([], dtype = self._enctype)

    # built-ins
    def __getitem__(self, item):
        arr = self._array[item]
        if arr.ndim == 0: arr = arr.reshape((1,))
        return self.__class__(array = arr)

    def __setitem__(self, key, value):
        self._array.__setitem__(key, self.encode(value))

    def __delitem__(self, key):
        self._array = np.delete(self._array, key)

    def __iter__(self):
        return iter(self.labels)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self._array == other.array
        elif listable(other):
            return self._array == self.encode(other)
        elif hashable(other):
            return self._array == self._levdct.get(other)
        else: raise TypeError('unsupported data type for comparison')

    def __contains__(self, item):
        oval = self._levdct.get(item)
        return oval in self._array

    def __add__(self, other):
        return self.insert(other)

    def __len__(self):
        return self.size

    def __str__(self):
        arr = self.labels
        if len(arr) > 10: arr = list(arr[:8]) + ['...'] + list(arr[-2:])
        s = '%s([%s], levels [%d] = %s)' % (self.__class__.__name__, join(arr, ', '), len(self._levdct), str(self.levels()))
        return s

    def __repr__(self):
        return str(self)

    # for numpy operators
    def __array__(self, dtype = None):
        arr = self.labels
        if dtype is not None: arr = arr.astype(dtype)
        return arr

    def __array_wrap__(self, arr):
        return self.__class__(labels = arr)

    # for pickle
    def __getstate__(self):
        return dict([(k, getattr(self, k)) for k in self.__slots__])

    def __setstate__(self, dct):
        for k in filter(lambda x: x in self.__slots__, dct.keys()): setattr(self, k, dct[k])

    # properties
    @property
    def labels(self):
        return self.decode(self._array)

    @property
    def array(self):
        return self._array.copy()

    @property
    def size(self):
        return self._array.shape[0]

    @property
    def shape(self):
        return self._array.shape

    @property
    def ndim(self):
        return 1

    # publics
    @classmethod
    def levels(cls):
        return cls._levdct.keys()

    @classmethod
    def values(cls):
        return cls._levdct.values()

    @classmethod
    def items(cls):
        return cls._levdct.items()

    @classmethod
    def encode(cls, labels):
        if isinstance(labels, cls.__class__):
            arr = labels.array
        elif listable(labels):
            arr = [cls._levdct[v] for v in labels]
        else:
            arr = [cls._levdct[labels]]
        return np.array(arr, dtype = cls._enctype)

    @classmethod
    def decode(cls, array):
        return np.array([cls._levdct.inv[v] for v in array], dtype = cls._sfmt)

    @classmethod
    def stack(cls, fct1, fct2):
        if not isinstance(fct1, cls) or not isinstance(fct2, cls): raise TypeError('unknown factor type(s)')
        return cls(array = np.hstack((fct1.array, fct2.array)))

    def insert(self, other, pos = NA):
        return self.__class__(array = np.insert(self._array, optional(pos, self.size), self.encode(other)))

    def drop(self, pos):
        return self.__class__(array = np.delete(self._array, pos))

    def put(self, ind, v, mode = 'raise'): # for np.narray.put
        v = self.encode(v)
        np.put(self._array, ind, v, mode = mode)

    def copy(self):
        return self.__class__(array = self._array)


def factor(name, levels, enctype = np.uint32):
    fct = type(name, (_Factor,), {})
    fct._enctype = enctype

    if mappable(levels): # dict is also listable
        if checkany(levels.values(), lambda x: not isinstance(x, int)): raise TypeError('level values are not integers')
        fct._levdct = FrozenOrderedBidict([(v, i) for v, i in levels.items()])
    elif listable(levels):
        if len(levels) != len(set(levels)): raise ValueError('levels have duplications')
        fct._levdct = FrozenOrderedBidict([(v, i) for i, v in enumerate(levels)])
    else:
        raise TypeError('unknown levels type: %s' % str(type(levels)))

    fct._sfmt = 'S%d' % max(map(len,levels))
    setattr(sys.modules[__name__], name, fct) # register to factor
    return fct

