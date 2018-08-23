#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
namedIndex

author(s): Albert (aki) Zhou
origin: 08-23-2018

"""


import numpy as np
from collections import OrderedDict
from kagami.core import NA, optional
from kagami.dtypes import coreType


class NamedIndex(coreType):
    def __init__(self, names = NA):
        self._ndict = NA
        self.names = optional(names, [])

    # built-ins
    def __getitem__(self, item):
        return NamedIndex(self.names.__getitem__(item))

    def __setitem__(self, key, value):
        nams = np.array(self)
        vals = np.array(value, dtype = str)
        nams.__setitem__(key, vals)
        self.names = nams

    def __delitem__(self, key):
        self.names = np.delete(self.names, key)

    def __iter__(self):
        return iter(self._ndict.keys())

    def __contains__(self, item):
        return self._ndict.has_key(item)

    def __eq__(self, other):
        return self.names == (other.names if isinstance(other, NamedIndex) else other)

    def __add__(self, other):
        return self.append(other)

    def __iadd__(self, other):
        bn = self.size
        for i,n in enumerate(other): self._ndict[str(n)] = bn + i

    def __len__(self):
        return self.size

    def __str__(self):
        return self.names.__str__()

    def __repr__(self):
        return self.names.__repr__()

    def __array__(self, dtype = None):
        return np.array(self._ndict.keys(), dtype = (object if dtype is None else dtype)) # object to avoid string size cutoff

    def __array_wrap__(self, arr):
        return NamedIndex(arr)

    # properties
    @property
    def names(self):
        return np.array(self, dtype = str)

    @names.setter
    def names(self, value):
        self._ndict = OrderedDict([(str(n),i) for i,n in enumerate(value)])
        if len(value) != len(self._ndict): raise KeyError('input names have duplications')

    @property
    def size(self):
        return len(self._ndict)

    @property
    def shape(self):
        return self.size,

    @property
    def ndim(self):
        return 1

    # public
    def namesOf(self, ids):
        return self.names[ids]

    def indicesOf(self, nams):
        return np.array([self._ndict[n] for n in nams])

    def append(self, other):
        idx = self.copy()
        idx += other
        return idx

    def insert(self, other, pos = NA):
        return NamedIndex(np.insert(np.array(self), optional(pos, self.size), other))

    def drop(self, pos):
        return NamedIndex(np.delete(np.array(self), optional(pos, self.size)))

    def copy(self):
        idx = NamedIndex()
        idx._ndict = self._ndict.copy()
        return idx

