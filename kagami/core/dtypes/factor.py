#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
factor

author(s): Albert (aki) Zhou
origin: 08-08-2018

"""


import numpy as np
from string import join
from bidict import FrozenOrderedBidict
from kagami.core.prelim import NA, hasvalue, optional, checkany, listable, mappable


class _Factor(object):
    __slots__ = ('_array', '_levdct', '_enctype')

    def __init__(self, array = NA, arrValues = NA):
        if hasvalue(array):
            self._array = np.array(self._mapLevel(array), dtype = self._enctype)
        elif hasvalue(arrValues):
            if checkany(arrValues, lambda x: x not in self._levdct.values()): raise ValueError('array values not recognised')
            self._array = np.array(arrValues, dtype = self._enctype)
        else:
            self._array = np.array([], dtype = self._enctype)

    # privates
    def _mapLevel(self, levels):
        if isinstance(levels, self.__class__):
            arr = levels.arrValues
        elif listable(levels):
            arr = [self._levdct[v] for v in levels]
        else:
            arr = self._levdct[levels]
        return arr

    # build-ins
    def __getitem__(self, item):
        return self.__class__(arrValues = self._array[item])

    def __setitem__(self, key, value):
        self._array.__setitem__(key, self._mapLevel(value))

    def __iter__(self):
        return iter(self.array)

    def __contains__(self, item):
        return item in self._levdct.keys()

    def __len__(self):
        return self.size

    def __str__(self):
        arr = self.array
        if len(arr) > 10: arr = list(arr[:8]) + ['...'] + list(arr[-2:])
        s = 'Factor[' + join(arr, ', ') + ']\n' + \
            'levels [%d]: %s' % (len(self._levdct), self.levels)
        return s

    def __repr__(self):
        return str(self)

    def __array__(self):
        return self.array

    # properties
    @property
    def levels(self):
        return self._levdct.keys()

    @property
    def values(self):
        return self._levdct.values()

    @property
    def items(self):
        return self._levdct.items()

    @property
    def array(self):
        return np.array([self._levdct.inv[v] for v in self._array])

    @property
    def arrValues(self):
        return self._array.copy()

    @property
    def size(self):
        return self._array.shape[0]

    # publics
    @classmethod
    def encode(cls, array):
        return np.array([cls._levdct[v] for v in array], dtype = cls._enctype)

    @classmethod
    def decode(cls, arrValues):
        return np.array([cls._levdct.inv[v] for v in arrValues])

    def insert(self, other, ids = NA):
        return self.__class__(arrValues = np.insert(self._array, optional(ids, self.size), self._mapLevel(other)))

    def drop(self, ids):
        return self.__class__(arrValues = np.delete(self._array, ids))


def factor(name, levels, enctype = np.uint32):
    fct = type(name, (_Factor,), {})

    if listable(levels):
        if len(levels) != len(set(levels)): raise ValueError('levels have duplications')
        fct._levdct = FrozenOrderedBidict([(v, i) for i, v in enumerate(levels)])
    elif mappable(levels):
        if checkany(levels.values(), lambda x: not isinstance(x, int)): raise TypeError('level values are not integers')
        fct._levdct = FrozenOrderedBidict([(v, i) for v, i in levels.items()])
    else:
        raise TypeError('unknown levels type: %s' % str(type(levels)))

    fct._enctype = enctype
    return fct

