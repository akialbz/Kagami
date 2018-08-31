#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
structArray

author(s): Albert (aki) Zhou
origin: 08-23-2018

"""


import numpy as np
from collections import OrderedDict
from kagami.core import NA, isna, hashable, checkany, listable
from kagami.dtypes import CoreType


class StructuredArray(CoreType):
    __slots__ = ('_dict', '_size')

    def __init__(self, *args, **kwargs):
        self._dict = OrderedDict(*args, **kwargs)
        self._size = NA
        for k,v in self._dict.items(): self[k] = v

    # privates
    def _parseIndices(self, idx):
        sids, aids = (idx, slice(None)) if not isinstance(idx, tuple) else \
                     (idx[0], slice(None)) if len(idx) == 1 else idx

        def _parse(ids, lst, kinds):
            if isinstance(ids, slice): return ids
            ids = np.array(ids)
            if ids.ndim != 1: ids = ids.reshape((1, -1))
            return ids if ids.dtype.kind in kinds else lst[ids]

        sids = _parse(sids, self.names(), ('S', 'U'))
        aids = _parse(aids, np.arange(self.shape[0]), ('i',))
        return sids, aids

    # built-ins
    def __getitem__(self, item):
        if hashable(item) and self._dict.has_key(item):
            value = self._dict[item]
        else:
            sids, aids = self._parseIndices(item)
            if isinstance(sids, slice): sids = self.names()[sids]
            value = StructuredArray([(k, self._dict[k][aids]) for k in sids])
        return value

    def __setitem__(self, key, value):
        if isinstance(value, StructuredArray):
            sids, aids = self._parseIndices(key)
            if isinstance(sids, slice): sids = self.names()[sids]
            for k in sids: self._dict[k][aids] = value[k]
        else:
            if not isinstance(value, CoreType): value = np.array(value)
            if value.ndim != 1: value = value.reshape((1,-1))
            if isna(self._size): self._size = len(value)
            elif len(value) != self._size: raise ValueError('index values size not match')
            self._dict[key] = value

    def __delitem__(self, key):
        sids, aids = self._parseIndices(key)
        if isinstance(sids, slice) and sids == slice(None): sids = []
        if isinstance(aids, slice) and aids == slice(None): aids = []

        if sids == [] and aids == []:
            self._dict = OrderedDict()
            self._size = NA
        else:
            if isinstance(sids, slice): sids = self.names()[sids]
            for k in sids: del self._dict[k]
            for k, v in self._dict.items(): self._dict[k] = np.delete(v, aids)

    def __iter__(self):
        return iter(self._dict.keys())

    def __contains__(self, item):
        return self._dict.has_key(item)

    def __len__(self):
        return len(self._dict)



    def __eq__(self, other):
        raise NotImplementedError('method not implemented for Kagami CoreType')

    def __add__(self, other):
        raise NotImplementedError('method not implemented for Kagami CoreType')

    def __iadd__(self, other):
        raise NotImplementedError('method not implemented for Kagami CoreType')

    def __str__(self):
        raise NotImplementedError('method not implemented for Kagami CoreType')

    def __repr__(self):
        raise NotImplementedError('method not implemented for Kagami CoreType')



    # properties
    @property
    def size(self):
        return self._size

    @property
    def shape(self):
        return len(self), self._size

    # publics
    def names(self):
        return np.array(self._dict.keys())

    def series(self):
        return np.array(self._dict.values())







    def insert(self, other, pos = NA):
        if not isinstance(other, _Index): raise TypeError('insert object is not Index')
        if checkany(self.keys(), lambda x: not other.has_key(x)): raise KeyError('index has different keys')
        if isna(pos): pos = self._size
        return _Index([(k, np.insert(v, pos, other[k])) for k,v in self.items()])

    def drop(self, pos):
        return _Index([(k, np.delete(v, pos)) for k,v in self.items()])

    def toList(self, transpose = False):
        olst = [[k] + list(v) for k,v in self.items()]
        return olst if not transpose else list(map(list,zip(*olst)))

    def copy(self):
        return _Index(self.items(), size = self._size)

