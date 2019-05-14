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
from kagami.core import na, optional, missing, listable, isstring, checkany, smap
from coreType import CoreType


__all__ = ['NamedIndex']


strtype_ = lambda x: isstring(x) if not listable(x) else all(smap(x,isstring))

class NamedIndex(CoreType):
    __slots__ = ('_names', '_ndict', '_fixrep')

    def __init__(self, names = na, fixRepeat = False):
        self._fixrep = fixRepeat
        self.names = optional(names, [])

    # built-ins
    def __getitem__(self, item):
        if isinstance(item, int): return self._names[item]
        return NamedIndex(self._names[item], fixRepeat = self._fixrep)

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
        return NamedIndex(arr, fixRepeat = self._fixrep)

    # properties
    @property
    def names(self):
        return self._names.copy()

    @names.setter
    def names(self, value):
        if isinstance(value, NamedIndex): self._names, self._ndict = value._names.copy(), value._ndict.copy(); return

        self._names = np.array(value, dtype = object)
        if self._names.ndim != 1: self._names = self._names.reshape((1,))
        if checkany(self._names, lambda x: not isstring(x)): raise TypeError('index names must be string')

        if self._fixrep:
            cdct = defaultdict(lambda: 1)
            for i,n in enumerate(self._names):
                count, cdct[n] = cdct[n], cdct[n] + 1
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

    @property
    def fixRepeat(self):
        return self._fixrep

    @fixRepeat.setter
    def fixRepeat(self, value):
        self._fixrep = bool(value)

    # public
    def namesof(self, ids):
        return self._names[ids]

    def idsof(self, nams):
        if not listable(nams): return self._ndict[nams]
        if len(nams) == 0: return np.array([])
        ids = np.array(itemgetter(*nams)(self._ndict))
        return ids if ids.ndim == 1 else ids.reshape((1,))

    def append(self, other):
        return NamedIndex(np.hstack((self._names, other)), fixRepeat = self._fixrep)

    def insert(self, other, pos = na):
        if missing(pos): pos = self.size
        elif strtype_(pos): pos = self.idsof(pos)
        return NamedIndex(np.insert(self._names, pos, other), fixRepeat = self._fixrep)

    def drop(self, pos):
        if missing(pos): pos = self.size
        elif strtype_(pos): pos = self.idsof(pos)
        return NamedIndex(np.delete(self._names, pos), fixRepeat = self._fixrep)

    def copy(self):
        idx = NamedIndex()
        idx._names = self._names.copy()
        idx._ndict = self._ndict.copy()
        idx._fixrep = self._fixrep
        return idx

