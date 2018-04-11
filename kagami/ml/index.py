#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
index: Dataset index class

author(s): Albert (aki) Zhou
origin: 02-18-2017

"""


import numpy as np
from operator import itemgetter
from copy import deepcopy
from ..prelim import NA, optional, hasvalue, isna, checkany, listable, mappable


# dataset index class
class _Index(object):
    def __init__(self, ids = NA, strfmt = 'S32', **kwargs):
        self._sfmt = strfmt

        ids = ids.items() if mappable(ids) else \
              ids.items if isinstance(ids, _Index) else \
              () if isna(ids) or ids is None else ids
        if checkany(ids, lambda x: not (listable(x) and len(x) == 2)): raise ValueError('unknown input indeices format')

        self._idct = {}
        for k,v in ids: self[k] = v
        for k,v in kwargs.items(): self[k] = v

    # privates
    def _parseKey(self, key, value = NA):
        rids, cids = (key, None) if not isinstance(key, tuple) else \
                     (key[0], None) if len(key) == 1 else key
        if isinstance(rids, slice):
            rids = itemgetter(rids)(self.names)
        else:
            if not listable(rids): rids = [rids]; value = [value] if hasvalue(value) else NA
            elif isinstance(rids[0], (bool, np.bool_)): rids = np.where(rids)[0]
            if not isinstance(rids[0], (str, unicode)): rids = itemgetter(*rids)(self.names)
        return (rids, cids, value) if hasvalue(value) else (rids, cids)

    # build-ins
    def __getitem__(self, item):
        rids, cids = self._parseKey(item)
        if cids is None: cids = slice(None)
        return _Index([(k, self._idct[k][cids]) for k in rids], strfmt = self._sfmt)

    def __setitem__(self, key, value):
        rids, cids, value = self._parseKey(key, value)
        if len(value) != len(rids): raise ValueError('index names and values number not match')

        if cids is None:
            value = [np.array(v if listable(v) else [v]) for v in value]
            vsize = self.ndim if self.size > 0 else len(value[0])
            if checkany(value, lambda x: len(x) != vsize): raise ValueError('index value sizes not match')
            for k, v in zip(rids, value): self._idct[k] = v.astype(self._sfmt) if v.dtype.kind in ('S', 'U') else v
        else:
            if checkany(rids, lambda x: x not in self): raise KeyError('index key not found')
            for k, v in zip(rids, value): self._idct[k][cids] = v

    def __add__(self, other):
        if not isinstance(other, _Index): raise TypeError('unknown behaviour to add Index and %s objects' % type(other).__name__)
        if set(self.names) != set(other.names): raise ValueError('indices have different names')
        return _Index({k: np.insert(v, len(v), other.values(k)) for k, v in self.items}, strfmt = self._sfmt)

    def __contains__(self, item):
        return self._idct.has_key(item)

    def __eq__(self, other):
        if not isinstance(other, _Index) or \
           set(self.names) != set(other.names) or \
           checkany(self.names, lambda x: not np.all(self.values(x) == other.values(x))): return False
        return True

    def __len__(self):
        return self.size

    def __str__(self):
        return self._idct.__str__()

    def __repr__(self):
        return self._idct.__repr__()

    # properties
    @property
    def names(self):
        return tuple(self._idct.keys())

    @property
    def indices(self):
        return tuple(self._idct.values())

    @property
    def items(self):
        return tuple(self._idct.items())

    @property
    def size(self):
        return len(self._idct)

    @property
    def ndim(self):
        return len(self._idct[self._idct.keys()[0]]) if self.size > 0 else NA

    @property
    def shape(self):
        return self.size, self.ndim

    # publics
    def values(self, key = NA):
        if self.size == 1: key = optional(key, self.names[0])
        elif isna(key): raise ValueError('index has multiple names')
        return self._idct[key]

    def where(self, key, cond):
        return np.where(cond(self.values(key)) if callable(cond) else self.values(key) == cond)[0]

    def insert(self, other, ids = NA):
        if set(self.names) != set(other.names): raise KeyError('indices have different names')
        ids = optional(ids, self.ndim)
        return _Index([(k, np.insert(v, ids, other.values(k))) for k, v in self.items], strfmt = self._sfmt)

    def drop(self, ids, axis = 0):
        if axis == 0:
            rids, _ = self._parseKey((ids,))
            return _Index({k: v for k, v in self.items if k not in rids}, strfmt = self._sfmt)
        elif axis == 1:
            return _Index({k: np.delete(v, ids) for k, v in self.items}, strfmt = self._sfmt)
        else: raise IndexError('unsupported axis %d' % axis)

    def copy(self):
        return deepcopy(self)
