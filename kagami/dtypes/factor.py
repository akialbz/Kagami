#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
factor

author(s): Albert (aki) Zhou
origin: 08-08-2018

"""


import sys, time
import numpy as np
from string import join
from operator import itemgetter
from bidict import FrozenOrderedBidict
from kagami.core import na, available, optional, checkany, listable, mappable, hashable, smap
from coreType import CoreType


__all__ = ['factor', 'asFactor']


# DO NOT call this class directly, use factor()
class _Factor(CoreType):
    __slots__ = ('_array', '_levdct', '_enctype', '_sfmt')

    def __init__(self, labels = na, array = na, _fromCopy = False):
        if available(labels):
            self._array = self.encode(labels)
        elif available(array):
            self._array = np.array(array, dtype = self._enctype)
            if self._array.ndim != 1: self._array = self._array.reshape((1,))
            if not _fromCopy and checkany(self._array, lambda x: x not in self._levdct.values()): raise ValueError('array values not recognised')
        else:
            self._array = np.array([], dtype = self._enctype)

    # built-ins
    def __getitem__(self, item):
        return self.__class__(array = self._array[item], _fromCopy = True)

    def __setitem__(self, key, value):
        self._array[key] = self.encode(value)

    def __delitem__(self, key):
        self._array = np.delete(self._array, key)

    def __iter__(self):
        return iter(self.labels)

    def __contains__(self, item):
        oval = self._levdct.get(item)
        return oval in self._array

    def __len__(self):
        return self.size

    def __eq__(self, other):
        return self._array == self.encode(other)

    def __iadd__(self, other):
        self._array = np.hstack((self._array, self.encode(other)))
        return self

    def __str__(self):
        return str(self.labels)

    def __repr__(self):
        rlns = str(self.labels).split('\n')

        cnam = self.__class__.__name__ + '('
        hdss = ' ' * len(cnam)
        rlns = [cnam + rlns[0]] + \
               [hdss + ln for ln in rlns[1:]] + \
               [hdss + 'size = %d, levels[%d] = %s)' % (self.size, len(self._levdct), str(self.levels()))]
        rlns[-2] += ','

        return join(rlns, '\n')

    # for numpy operators
    def __array__(self, dtype = None):
        arr = self.labels
        return arr if dtype is None else arr.astype(dtype)

    def __array_wrap__(self, arr):
        return self.__class__(labels = arr)

    # properties
    @property
    def labels(self):
        arr = np.array(itemgetter(*self._array)(self._levdct.inv), dtype = self._sfmt)
        return arr if arr.ndim == 1 else arr.reshape((1,))

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
        if isinstance(labels, cls):
            return labels.array
        elif listable(labels):
            arr = np.array(itemgetter(*labels)(cls._levdct) if len(labels) > 0 else [], dtype = cls._enctype)
            return arr if arr.ndim == 1 else arr.reshape((1,))
        elif hashable(labels):
            return np.array([cls._levdct[labels]], dtype = cls._enctype)
        else: raise TypeError('unsupported data type for labels')

    @classmethod
    def decode(cls, array):
        if isinstance(array, cls):
            return array.labels
        elif listable(array):
            lab = np.array(itemgetter(*array)(cls._levdct.inv) if len(array) > 0 else [], dtype = cls._sfmt)
            return lab if lab.ndim == 1 else lab.reshape((1,))
        elif hashable(array):
            return np.array([cls._levdct.inv[array]], dtype = cls._sfmt)
        else: raise TypeError('unsupported data type for array')

    def append(self, other):
        return self.__class__(array = np.hstack((self._array, self.encode(other))), _fromCopy = True)

    def insert(self, other, pos = na):
        return self.__class__(array = np.insert(self._array, optional(pos, self.size), self.encode(other)), _fromCopy = True)

    def drop(self, pos):
        return self.__class__(array = np.delete(self._array, pos), _fromCopy = True)

    def copy(self):
        return self.__class__(array = self._array, _fromCopy = True)


# factor interface
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

    fct.__slots__ += tuple(fct._levdct.keys())
    for k,v in fct._levdct.items(): setattr(fct, k, v)

    fct._sfmt = 'S%d' % max(smap(levels, len))
    setattr(sys.modules[__name__], name, fct) # register to factor
    return fct

def asFactor(labels, levels = na, enctype = np.uint32):
    fcls = factor(name = '_factor_%s' % hex(int(time.time())), levels = optional(levels, np.unique(labels)), enctype = enctype)
    return fcls(labels)

