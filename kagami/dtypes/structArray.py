#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
structArray

author(s): Albert (aki) Zhou
origin: 08-23-2018

"""


import logging
import numpy as np
from string import join
from collections import OrderedDict
from types import NoneType
from kagami.core import NA, NAType, isna, checkall, checkany, listable, isstring, mappable, autoeval
from kagami.portals import tablePortal
from kagami.dtypes import CoreType


class StructuredArray(CoreType):
    __slots__ = ('_dict', '_length')

    def __init__(self, items = NA, **kwargs):
        items = items if listable(items) and checkall(items, lambda x: len(x) == 2) else \
                items._dict.items() if isinstance(items, StructuredArray) else \
                items.items() if mappable(items) else \
                kwargs.items() if isna(items) else NA
        if isna(items): raise TypeError('unknow data type')

        self._dict = OrderedDict()
        self._length = NA
        for k,v in items(): self[k] = v

    # privates
    def _parseIndices(self, idx, mapNames = True):
        sids, aids = (idx, slice(None)) if not isinstance(idx, tuple) else \
                     (idx[0], slice(None)) if len(idx) == 1 else idx

        def _wrap(ids):
            if isinstance(ids, slice): return ids
            ids = np.array(ids)
            if ids.ndim != 1: ids = ids.reshape((1,))
            return ids
        sids, aids = map(_wrap, (sids, aids))

        if (mapNames and isinstance(sids, slice)) or sids.dtype.kind not in ('S', 'U'): sids = self.names[sids]
        return sids, aids

    # built-ins
    def __getitem__(self, item):
        if isstring(item): return self._dict[item]
        sids, aids = self._parseIndices(item)
        return StructuredArray([(k, self._dict[k][aids]) for k in sids])

    def __setitem__(self, key, value):
        if isstring(key):
            if not isinstance(value, CoreType): value = np.array(value)
            if value.ndim != 1: raise ValueError('input value not in 1-dimensional')

            if isna(self._length): self._length = len(value)
            elif self._length != len(value): raise ValueError('input value size not match')

            self._dict[key] = value
        else:
            sids, aids = self._parseIndices(key)
            if not isinstance(value, CoreType): value = np.array(value, dtype = object)

            if value.ndim in (0, 1):
                for k in sids: self._dict[k][aids] = value
            elif value.ndim == 2:
                if len(sids) != len(value): raise ValueError('input names and values size not match')
                for k,nv in zip(sids, value): self._dict[k][aids] = nv
            else: raise IndexError('input values dimension too high')

    def __delitem__(self, key):
        if isstring(key): del self._dict[key]; return

        sids, aids = self._parseIndices(key, mapNames = False)
        slic, alic = sids == slice(None), aids == slice(None)

        if slic and alic:
            self._dict = OrderedDict()
            self._length = NA
        elif slic and not alic:
            for k in self.names: self._dict[k] = np.delete(self._dict[key], aids)
            self._length = len(self._dict[self._dict.keys()[0]])
        elif not slic and alic:
            for k in self.names[sids]: del self._dict[k]
        else: raise IndexError('unable to delete portion of the array')

    def __iter__(self):
        return iter(self._dict.keys())

    def __contains__(self, item):
        return self._dict.has_key(item)

    def __len__(self):
        return self.size

    def __eq__(self, other):
        if not isinstance(other, CoreType): other = np.array(other)
        if other.ndim == 2 and other.shape != self.shape: raise TypeError('comparison between data with different shapes')
        if isinstance(other, StructuredArray): return np.all(self.names == other.names) and np.all(self.values == other.values)
        return self.values == other

    def __iadd__(self, other):
        if not isinstance(other, StructuredArray): raise TypeError('unknown input data type')
        if self.size != other.size or not np.all(np.unique(self.names) == np.unique(other.names)): raise ValueError('input array has different names')
        for k, v in self._dict.items(): self._dict[k] = v.append(other[k]) if isinstance(v, CoreType) else np.r_[v, other[k].astype(v.dtype)]
        self._length += other.length
        return self

    def __str__(self):
        nptn = '%%%ds' % max(map(len, self.names))
        return join(map(str, [nptn % k + ' : ' + str(v) for k,v in zip(self.names, self.values)]), '\n')

    def __repr__(self):
        rlns = str(self).split('\n')
        rlns = ['StructuredArray(' + rlns[0]] + \
               ['                ' + ln for ln in rlns[1:]]
        return join(rlns, '\n') + ', size = (%d, %d))' % (self.size, self.length)

    # for numpy
    def __array__(self, dtype = None):
        arr = self.values
        return arr if dtype is None else arr.astype(None)

    # for pickle
    def __getstate__(self):
        return {k: getattr(self, k) for k in self.__slots__}

    def __setstate__(self, dct):
        for k in filter(lambda x: x in self.__slots__, dct.keys()): setattr(self, k, dct[k])

    # properties
    @property
    def names(self):
        return np.array(self._dict.keys())

    @property
    def series(self):
        return tuple(self._dict.values())

    @property
    def values(self):
        return np.array(map(np.array, self._dict.values()), dtype = object)

    @property
    def size(self):
        return len(self._dict)

    @property
    def length(self):
        return self._length

    @property
    def shape(self):
        return self.size, self.length

    @property
    def ndim(self):
        return 2

    # publics
    def append(self, other):
        if not isinstance(other, StructuredArray): raise TypeError('unknown input data type')
        if self.size != other.size or not np.all(np.unique(self.names) == np.unique(other.names)): raise ValueError('input array has different names')
        return StructuredArray([(k, v.append(other[k]) if isinstance(v, CoreType) else np.r_[v, other[k].astype(v.dtype)]) for k,v in self._dict.items()])

    def insert(self, other, pos = NA):
        if not isinstance(other, StructuredArray): raise TypeError('unknown input data type')
        if self.size != other.size or not np.all(np.unique(self.names) == np.unique(other.names)): raise ValueError('input array has different names')
        if isna(pos): pos = self.length
        return StructuredArray([(k, v.insert(other[k], pos) if isinstance(v, CoreType) else np.insert(v, pos, other[k])) for k,v in self._dict.items()])

    def drop(self, pos):
        return StructuredArray([(k, v.drop(pos) if isinstance(v, CoreType) else np.delete(v, pos)) for k,v in self._dict.items()])

    def copy(self):
        arr = StructuredArray()
        arr._dict = self._dict.copy()
        arr._length = self._length
        return arr

    # file portals
    @classmethod
    def loadFromCSV(cls, fname, delimiter = ','):
        dm = np.array(tablePortal.load(fname, delimiter = delimiter))
        nams, vals = dm[:,0].T[0], dm[:,1:]

        vdts = map(lambda x: type(autoeval(x[0])), vals)
        if checkany(vdts, lambda x: x in (NAType, NoneType)): logging.warning('invalid data type detected')
        vals = map(lambda x: np.array(x[0]).astype(x[1]), zip(vals, vdts))

        return StructuredArray([(k, v) for k,v in zip(nams, vals)])

    def saveToCSV(self, fname, delimiter = ','):
        odm = [[k] + map(str, self[k]) for k in self.names]
        tablePortal.save(odm, fname, delimiter = delimiter)

    @classmethod
    def loadFromHDF5(cls, fname):
        pass

    def saveToHDF5(self, fname):
        pass

