#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
structArray

author(s): Albert (aki) Zhou
origin: 08-23-2018

"""


from __future__ import annotations

import os
import numpy as np
import tables as tb
from typing import List, Tuple, Iterable, Mapping, Union, Optional, Any
from operator import itemgetter
from collections import OrderedDict
from kagami.common import l, ll, available, missing, checkall, iterable, listable, ismapping, isstring, smap, unpack, paste, checkInputFile, checkOutputFile
from kagami.portals import tablePortal
from .coreType import CoreType, Indices2D


__all__ = ['StructuredArray']


class StructuredArray(CoreType):
    __slots__ = ('_arrs', '_length')

    def __init__(self, items: Optional[Union[Iterable, Mapping, np.ndarray, StructuredArray]] = None, **kwargs: Iterable):
        if isinstance(items, StructuredArray): self._arrs, self._length = items._arrs.copy(), items._length; return

        vals = [items[k] for k in items.dtype.names] if isinstance(items, np.ndarray) and available(items.dtype.names) else \
               items.items()  if ismapping(items) else \
               items          if iterable(items) else \
               kwargs.items() if missing(items) else None
        if missing(vals): raise TypeError('unknow data type')

        self._arrs = OrderedDict()
        self._length = None
        for k,v in vals: self[k] = v

    # privates
    def _parseids(self, idx, mapslice = True):
        sids, aids = (idx, slice(None)) if not isinstance(idx, tuple) else \
                     (idx[0], slice(None)) if len(idx) == 1 else idx

        def _wrap(ids):
            if isinstance(ids, slice): return ids
            if not listable(ids): return [ids]
            return ids
        sids, aids = smap((sids, aids), _wrap)

        if mapslice: sids = self.names[sids]
        return sids, aids

    def _parsevals(self, value):
        if not iterable(value): return value
        if isinstance(value, StructuredArray): return [value._arrs[n].copy() for n in self._arrs.keys()]

        _wrap = lambda x: np.array(ll(x))
        value = ll(value)
        if not iterable(value[0]): return _wrap(value)

        value = smap(value, _wrap)
        if not len(set(smap(value, len))) == 1: raise ValueError('input arrays not in the same size')
        return value

    # built-ins
    def __getitem__(self, item):
        return self.take(item)

    def __setitem__(self, key, value):
        self.put(key, value, inline = True)

    def __delitem__(self, key):
        self.delete(key, inline = True)

    def __iter__(self):
        return self._arrs.keys()

    def __contains__(self, item):
        return item in self._arrs

    def __len__(self):
        return self.size

    def __eq__(self, other):
        if isinstance(other, StructuredArray):
            equ = self.shape == other.shape and \
                  set(self._arrs.keys()) == set(other._arrs.keys()) and \
                  checkall(self._arrs.keys(), lambda k: np.all(self._arrs[k] == other._arrs[k]))
        else:
            equ = self.arrays == np.array(other, dtype = object)
        return equ

    def __str__(self):
        nlen = max(smap(self._arrs.keys(), len))
        olns = [(('{'+f':{nlen}s'+'} : ').format(k) if i == 0 else (' ' * (nlen + 3))) + ln
                for k,v in zip(self._arrs.keys(), smap(self._arrs.values(), str)) for i,ln in enumerate(v.split('\n'))]
        return paste(*olns, sep = '\n')

    def __repr__(self):
        rlns = str(self).split('\n')
        rlns = ['StructuredArray(' + rlns[0]] + \
               ['                ' + ln for ln in rlns[1:]]
        return paste(*rlns, sep = '\n') + ', size = (%d, %d))' % (self.size, self.length)

    # for numpy
    def __array__(self, dtype = None):
        if available(dtype): return np.array(self.arrays, dtype = dtype)
        arr = np.array([*zip(*self._arrs.values())],
                       dtype = [(n, v.dtype.str) for n,v in zip(self._arrs.keys(), self._arrs.values())])
        return arr

    def __array_wrap__(self, arr):
        if missing(arr.dtype.names): raise TypeError('cannot assign non-structured ndarray to StructuredArray')
        return StructuredArray(arr)

    # properties
    @property
    def names(self) -> np.ndarray:
        return np.array(l(self._arrs.keys()))

    @property
    def arrays(self) -> List[np.ndarray]:
        return l(self._arrs.values())

    @property
    def fields(self) -> List[Tuple[str, np.ndarray]]:
        return l(self._arrs.items())

    @property
    def size(self) -> int:
        return len(self._arrs)

    @property
    def length(self) -> int:
        return self._length

    @property
    def shape(self) -> Tuple[int, int]:
        return self.size, self.length

    @property
    def ndim(self) -> int:
        return 2

    # publics
    def take(self, pos: Union[str, Indices2D]) -> StructuredArray:
        if isstring(pos): return self._arrs[pos]
        sids, aids = self._parseids(pos)
        return StructuredArray([(k, self._arrs[k][aids]) for k in sids])

    def put(self, pos: Union[str, Indices2D], value: Any, inline: bool = True) -> StructuredArray:
        narr = self if inline else self.copy()
        vals = self._parsevals(value)

        if isstring(pos):
            if not isinstance(vals, np.ndarray): raise ValueError('input array not in 1-dimensional')
            if missing(narr._length): narr._length = vals.size
            elif narr._length != vals.size: raise ValueError('input array size not match')
            narr._arrs[pos] = vals
        else:
            sids, aids = self._parseids(pos)
            if not isinstance(vals, list):
                for k in sids: narr._arrs[k][aids] = vals
            else:
                if len(sids) != len(vals): raise ValueError('input names and values size not match')
                for k,vals in zip(sids, vals): narr._arrs[k][aids] = vals
        return narr

    def append(self, value: Iterable[Iterable], inline: bool = True) -> StructuredArray:
        narr = self if inline else self.copy()
        vals = self._parsevals(value)
        if not isinstance(vals, list) or len(vals) != narr.size: raise ValueError('input values size not match')
        for k,v in narr._arrs.items(): narr._arrs[k] = np.r_[v, vals[k]]
        narr._length += vals[0].size
        return narr

    def insert(self, pos: Indices2D, value: Iterable[Iterable], inline: bool = True) -> StructuredArray:
        narr = self if inline else self.copy()
        vals = self._parsevals(value)
        if not isinstance(vals, list) or len(vals) != narr.size: raise ValueError('input values size not match')
        for k,v in narr._arrs.items(): narr._arrs[k] = np.insert(v, pos, vals[k])
        narr._length += vals[0].size
        return narr

    def delete(self, pos: Indices2D, inline: bool = True) -> StructuredArray:
        narr = self if inline else self.copy()
        if isstring(pos): del narr._arrs[pos]; return narr

        sids, aids = self._parseids(pos, mapslice = False)
        slic = isinstance(sids, slice) and sids == slice(None)
        alic = isinstance(aids, slice) and aids == slice(None)

        if slic and alic:
            narr._arrs = OrderedDict()
            narr._length = None
        elif slic and not alic:
            for k,v in narr._arrs.items(): narr._arrs[k] = np.delete(v, aids)
            narr._length = len(narr._arrs[l(narr._arrs.keys())[0]])
        elif not slic and alic:
            if isinstance(sids, slice) or sids.dtype.kind not in ('S', 'U'): sids = narr.names[sids]
            for k in sids: del narr._arrs[k]
        else: raise IndexError('unable to delete portion of the array')

        return narr

    def tolist(self) -> List[Tuple[str, np.ndarray]]:
        return self.fields

    def tostring(self) -> str:
        return str(self)

    def copy(self) -> StructuredArray:
        narr = StructuredArray()
        narr._arrs = self._arrs.copy()
        narr._length = self._length
        return narr

    # file portals
    @classmethod
    def fromsarray(cls, array: Iterable[Iterable[str]]):
        if not isinstance(array, np.ndarray): array = np.array(smap(array, ll))
        nams, vals = array[:,0], array[:,1:]
        nams, vdts = itemgetter(0, -1)(l(zip(*smap(nams, lambda x: x.lstrip('<').rstrip('>').partition('::')))))
        vals = smap(zip(vals,vdts), unpack(lambda v,d: np.array(v).astype(d)))
        return StructuredArray(zip(nams, vals))

    def tosarray(self):
        return np.array([np.r_[[f'<{k}::{v.dtype.descr.kind}>'], v.astype(str)] for k,v in self._arrs.items()])

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
        desc = type('_struct_array', (tb.IsDescription,), {n: tb.Col.from_dtype(v.dtype) for n,v in self._arrs.items()})
        tabl = tb.Table(root, tabname, desc)
        tabl.append([self._arrs[n] for n in tabl.colnames]) # desc.columns is an un-ordered dict
        tabl.attrs.names = self.names
        return tabl

    @classmethod
    def loadhdf(cls, fname):
        checkInputFile(fname)
        with tb.open_file(fname, mode = 'r') as hdf: arr = cls.fromhtable(hdf.root.StructuredArray)
        return arr

    def savehdf(self, fname, compression = 0):
        checkOutputFile(fname)
        with tb.open_file(fname, mode = 'w', filters = tb.Filters(compression)) as hdf: self.tohtable(hdf.root, 'StructuredArray')
        return os.path.isfile(fname)
