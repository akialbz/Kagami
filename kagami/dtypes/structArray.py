#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
structArray

author(s): Albert (aki) Zhou
origin: 08-23-2018

"""


import logging, os
import numpy as np
import tables as ptb
from string import join
from collections import OrderedDict
from types import NoneType
from kagami.core import na, NAType, missing, checkall, checkany, listable, isstring, mappable, autoeval, smap, pickmap, unpack, checkInputFile, checkOutputFile
from kagami.portals import tablePortal
from coreType import CoreType


__all__ = ['StructuredArray']


class StructuredArray(CoreType):
    __slots__ = ('_dict', '_length')

    def __init__(self, items = na, **kwargs):
        items = items if listable(items) and checkall(items, lambda x: len(x) == 2) else \
                items._dict.items() if isinstance(items, StructuredArray) else \
                items.items() if mappable(items) else \
                kwargs.items() if missing(items) else na
        if missing(items): raise TypeError('unknow data type')

        self._dict = OrderedDict()
        self._length = na
        for k,v in items: self[k] = v

    # privates
    def _parseIndices(self, idx, mapNames = True):
        sids, aids = (idx, slice(None)) if not isinstance(idx, tuple) else \
                     (idx[0], slice(None)) if len(idx) == 1 else idx

        def _wrap(ids):
            if isinstance(ids, slice): return ids
            ids = np.array(ids)
            if ids.ndim != 1: ids = ids.reshape((1,))
            return ids
        sids, aids = smap((sids, aids), _wrap)

        if mapNames and (isinstance(sids, slice) or sids.dtype.kind not in ('S', 'U')): sids = self.names[sids]
        return sids, aids

    # built-ins
    def __getitem__(self, item):
        if isstring(item): return self._dict[item]
        sids, aids = self._parseIndices(item)
        return StructuredArray([(k, self._dict[k][aids]) for k in sids])

    def __setitem__(self, key, value):
        if isstring(key):
            if isinstance(value, np.ndarray) and (value.dtype.kind == 'u' or (value.dtype.kind == 'i' and value.dtype.itemsize < 8)):
                logging.warning('special integer dtype may cause na comparison failure')

            value = value.copy() if isinstance(value, CoreType) else np.array(value)
            if value.ndim != 1: raise ValueError('input value not in 1-dimensional')

            if missing(self._length): self._length = len(value)
            elif self._length != len(value): raise ValueError('input value size not match')

            self._dict[key] = value
        else:
            sids, aids = self._parseIndices(key)
            if not isinstance(value, CoreType): value = np.array(value, dtype = object)

            if value.ndim in (0, 1):
                for k in sids: self._dict[k][aids] = value
            elif value.ndim == 2:
                if len(sids) != len(value): raise ValueError('input names and values size not match')
                if isinstance(value, StructuredArray):
                    if not np.all(value.names == self.names): raise KeyError('input array has different names')
                    value = value.series
                for k,nv in zip(sids, value): self._dict[k][aids] = nv
            else: raise IndexError('input values dimension too high')

    def __delitem__(self, key):
        if isstring(key): del self._dict[key]; return

        sids, aids = self._parseIndices(key, mapNames = False)
        slic = isinstance(sids, slice) and sids == slice(None)
        alic = isinstance(aids, slice) and aids == slice(None)

        if slic and alic:
            self._dict = OrderedDict()
            self._length = na
        elif slic and not alic:
            for k in self.names: self._dict[k] = np.delete(self._dict[k], aids)
            self._length = len(self._dict[self._dict.keys()[0]])
        elif not slic and alic:
            if isinstance(sids, slice) or sids.dtype.kind not in ('S', 'U'): sids = self.names[sids]
            for k in sids: del self._dict[k]
        else: raise IndexError('unable to delete portion of the array')

    def __iter__(self):
        return iter(self._dict.keys())

    def __contains__(self, item):
        return self._dict.has_key(item)

    def __len__(self):
        return self.size

    def __eq__(self, other):
        if not isinstance(other, StructuredArray): return self.values == np.array(other, dtype = object)
        return self.shape == other.shape and np.all(np.sort(self._dict.keys()) == np.sort(other._dict.keys())) and \
               checkall(self._dict.keys(), lambda k: np.all(self._dict[k] == other[k]))

    def __iadd__(self, other):
        if not isinstance(other, StructuredArray): raise TypeError('unknown input data type')
        if self.size != other.size or not np.all(self.names == other.names): raise KeyError('input array has different names')
        for k, v in self._dict.items(): self._dict[k] = v.append(other[k]) if isinstance(v, CoreType) else np.r_[v, other[k].astype(v.dtype)]
        self._length += other.length
        return self

    def __str__(self):
        nptn = '%%%ds' % max(smap(self.names, len))
        return join([nptn % k + ' : ' + str(v) for k,v in zip(self.names, self.values)], '\n')

    def __repr__(self):
        rlns = str(self).split('\n')
        rlns = ['StructuredArray(' + rlns[0]] + \
               ['                ' + ln for ln in rlns[1:]]
        return join(rlns, '\n') + ', size = (%d, %d))' % (self.size, self.length)

    # for numpy
    def __array__(self, dtype = None):
        arr = self.values
        return arr if dtype is None else arr.astype(dtype)

    # properties
    @property
    def names(self):
        return np.array(self._dict.keys())

    @property
    def values(self):
        return np.array(smap(self.series, np.array), dtype = object)

    @property
    def series(self):
        return self._dict.values()

    @property
    def items(self):
        return self._dict.items()

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
        if self.size != other.size or not np.all(np.unique(self.names) == np.unique(other.names)): raise KeyError('input array has different names')
        return StructuredArray([(k, v.append(other[k]) if isinstance(v, CoreType) else np.r_[v, other[k].astype(v.dtype)]) for k,v in self._dict.items()])

    def insert(self, other, pos = na):
        if not isinstance(other, StructuredArray): raise TypeError('unknown input data type')
        if self.size != other.size or not np.all(np.unique(self.names) == np.unique(other.names)): raise KeyError('input array has different names')
        if missing(pos): pos = self.length
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
    def fromsarray(cls, array):
        nams, vals = array[:,0], array[:,1:]

        nams = pickmap(nams, lambda x: x[0] == '<' and x[-1] == '>', lambda x: x[1:-1])

        vdts = smap(vals, lambda x: type(autoeval(x[0])))
        if checkany(vdts, lambda x: x in (NAType, NoneType)): logging.warning('invalid data type detected')
        vals = smap(zip(vals, vdts), unpack(lambda v,d: np.array(v).astype(d) if d != bool else (np.array(v) == 'True')))

        return StructuredArray([(k, v) for k,v in zip(nams, vals)])

    def tosarray(self):
        return np.array([np.r_[['<%s>' % k], np.array(v, dtype = str)] for k,v in self._dict.items()])

    @classmethod
    def loadcsv(cls, fname, delimiter = ',', transposed = False):
        idm = np.array(tablePortal.load(fname, delimiter = delimiter))
        if transposed: idm = idm.T
        return cls.fromsarray(idm)

    def savecsv(self, fname, delimiter = ',', transpose = False):
        odm = self.tosarray()
        if transpose: odm = odm.T
        tablePortal.save(odm, fname, delimiter = delimiter)

    @classmethod
    def fromhtable(cls, hdftable):
        nams = hdftable.attrs.names
        vals = [np.array(hdftable.colinstances[n]) for n in nams]
        return StructuredArray(zip(nams, vals))

    def tohtable(self, root, tabname):
        vdct = {n: v for n,v in zip(self._dict.keys(), smap(self._dict.values(), np.array))}
        desc = type('_struct_array', (ptb.IsDescription,), {n: ptb.Col.from_dtype(v.dtype) for n,v in vdct.items()})
        tabl = ptb.Table(root, tabname, desc)
        tabl.append([vdct[n] for n in tabl.colnames]) # desc.columns is an un-ordered dict
        tabl.attrs.names = self._dict.keys()
        return tabl

    @classmethod
    def loadhdf(cls, fname):
        checkInputFile(fname)
        with ptb.open_file(fname, mode = 'r') as hdf: arr = cls.fromhtable(hdf.root.StructuredArray)
        return arr

    def savehdf(self, fname, compression = 0):
        checkOutputFile(fname)
        with ptb.open_file(fname, mode = 'w', filters = ptb.Filters(compression)) as hdf: self.tohtable(hdf.root, 'StructuredArray')
        return os.path.isfile(fname)
