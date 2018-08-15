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
from kagami.core.prelim import NA, hasvalue, optional, checkany, listable, mappable, hashable


class _Factor(object):
    __slots__ = ('_array', '_levdct', '_enctype')

    def __init__(self, array = NA, arrValues = NA):
        if hasvalue(array):
            self._array = self.encode(array)
        elif hasvalue(arrValues):
            if checkany(set(arrValues), lambda x: x not in self._levdct.values()): raise ValueError('array values not recognised')
            self._array = np.array(arrValues, dtype = self._enctype)
        else:
            self._array = np.array([], dtype = self._enctype)

    # build-ins
    def __getitem__(self, item):
        return self.__class__(arrValues = self._array[item])

    def __setitem__(self, key, value):
        self._array.__setitem__(key, self.encode(value))

    def __iter__(self):
        return iter(self.array)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self._array == other.arrValues
        elif listable(other):
            return self._array == self.encode(other)
        elif hashable(other):
            return self._array == self._levdct.get(other)
        else: raise TypeError('unsupported data type for comparison')

    def __ne__(self, other):
        return ~self.__eq__(other)

    def __contains__(self, item):
        oval = self._levdct.get(item)
        return oval in self._array

    def __add__(self, other):
        return self.insert(other)

    def __len__(self):
        return self.size

    def __str__(self):
        arr = self.array
        if len(arr) > 10: arr = list(arr[:8]) + ['...'] + list(arr[-2:])
        s = '%s([%s], levels [%d] = %s)' % (self.__class__.__name__, join(arr, ', '), len(self._levdct), str(self.levels()))
        return s

    def __repr__(self):
        return str(self)

    # for numpy operators
    def __array__(self, dtype = None):
        arr = self.array
        if dtype is not None: arr = arr.astype(dtype)
        return arr

    def __array_wrap__(self, arr):
        return self.__class__(array = arr)

    # for pickle
    def __getstate__(self):
        return dict([(k, getattr(self, k)) for k in self.__slots__])

    def __setstate__(self, dct):
        for k in filter(lambda x: x in self.__slots__, dct.keys()): setattr(self, k, dct[k])

    # properties
    @property
    def array(self):
        return self.decode(self._array)

    @property
    def arrValues(self):
        return self._array.copy()

    @property
    def size(self):
        return self._array.shape[0]

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
    def encode(cls, array):
        if isinstance(array, cls.__class__):
            arr = array.arrValues
        elif listable(array):
            arr = [cls._levdct[v] for v in array]
        else:
            arr = cls._levdct[array]
        return np.array(arr, dtype = cls._enctype)

    @classmethod
    def decode(cls, arrValues):
        return np.array([cls._levdct.inv[v] for v in arrValues])

    @classmethod
    def stack(cls, fct1, fct2):
        if not isinstance(fct1, cls) or not isinstance(fct2, cls): raise TypeError('unknown factor type(s)')
        return cls(arrValues = np.hstack((fct1.arrValues, fct2.arrValues)))

    def insert(self, other, ids = NA):
        return self.__class__(arrValues = np.insert(self._array, optional(ids, self.size), self.encode(other)))

    def drop(self, ids):
        return self.__class__(arrValues = np.delete(self._array, ids))

    def copy(self):
        return self.__class__(arrValues = self._array)


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

    setattr(sys.modules[__name__], name, fct) # register to factor
    return fct

