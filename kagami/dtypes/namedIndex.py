#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
namedIndex

author(s): Albert (aki) Zhou
origin: 08-23-2018

"""


import numpy as np
from operator import itemgetter
from collections import defaultdict
from string import join
from kagami.core import na, optional, listable, isstring, checkany, pickmap
from kagami.dtypes import CoreType


__all__ = ['NamedIndex']


class NamedIndex(CoreType):
    __slots__ = ('_names', '_ndict', '_relabel')

    def __init__(self, names = na, relabel = False):
        self._relabel = relabel
        self.names = optional(names, [])

    # built-ins
    def __getitem__(self, item):
        return NamedIndex(self._names[item])

    def __setitem__(self, key, value):
        self._names[key] = value
        self.names = self._names

    def __delitem__(self, key):
        self.names = np.delete(self._names, key)

    def __iter__(self):
        return iter(self._names)

    def __contains__(self, item):
        return self._ndict.has_key(item)

    def __len__(self):
        return self.size

    def __eq__(self, other):
        return self._names == np.array(other, dtype = object)

    def __iadd__(self, other):
        if not listable(other): other = [other]
        if checkany(other, lambda x: not isstring(x)): raise TypeError('index names must be string')

        size = self.size
        self._names = np.r_[self._names, other]
        for i,n in enumerate(other): self._ndict[n] = size + i
        if self._names.shape[0] != len(self._ndict): raise KeyError('input names have duplications')
        return self

    def __str__(self):
        return str(self._names)

    def __repr__(self):
        rlns = str(self._names).split('\n')
        rlns = ['NamedIndex(' + rlns[0]] + \
               ['           ' + ln for ln in rlns[1:]]
        return join(rlns, '\n') + ', size = %d)' % self.size

    # for numpy
    def __array__(self, dtype = None):
        return self._names.astype(str) if dtype is None else self._names.astype(dtype)

    def __array_wrap__(self, arr):
        return NamedIndex(arr)

    # properties
    @property
    def names(self):
        return self._names.copy()

    @names.setter
    def names(self, value):
        self._names = np.array(value, dtype = object)
        if self._names.ndim != 1: self._names = self._names.reshape((1,))
        if checkany(self._names, lambda x: not isstring(x)): raise TypeError('index names must be string')

        if self._relabel:
            cdct = defaultdict(lambda: 1)
            for i,c in enumerate(self._names):
                count, cdct[c] = cdct[c], cdct[c] + 1
                if count > 1: self._names[i] += '.%d' % count # self._names is an object array

        self._ndict = {n:i for i,n in enumerate(self._names)} # much faster than dict()
        if self._names.shape[0] != len(self._ndict): raise KeyError('input names have duplications')

    @property
    def size(self):
        return self._names.shape[0]

    @property
    def shape(self):
        return self._names.shape

    @property
    def ndim(self):
        return 1

    # public
    def namesof(self, ids):
        return self._names[ids]

    def idsof(self, nams):
        if not listable(nams): nams = [nams]
        ids = np.array(itemgetter(*nams)(self._ndict))
        return ids if ids.ndim == 1 else ids.reshape((1,))

    def append(self, other):
        return NamedIndex(np.hstack((self._names, other)))

    def insert(self, other, pos = na):
        return NamedIndex(np.insert(self._names, optional(pos, self.size), other))

    def drop(self, pos):
        return NamedIndex(np.delete(self._names, optional(pos, self.size)))

    def copy(self):
        idx = NamedIndex()
        idx._names = self._names.copy()
        idx._ndict = self._ndict.copy()
        return idx

