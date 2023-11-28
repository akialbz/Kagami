#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
structArray

author(s): Albert (aki) Zhou
added: 08-23-2018

"""


from __future__ import annotations

import os, re
import numpy as np
import pandas as pd
import tables as tb
from typing import List, Tuple, Iterable, Mapping, Union, Optional, Any
from pathlib import Path
from collections import OrderedDict
from kagami.comm import l, ll, available, missing, checkall, checkany, iterable, listable, ismapping, isstring, smap, unpack, paste, checkInputFile, checkOutputFile
from kagami.portals import tablePortal
from .coreType import CoreType, Indices, Indices2D


__all__ = ['StructuredArray']


class StructuredArray(CoreType):
    __slots__ = ('_arrs', '_length')

    def __init__(self, items: Optional[Union[Iterable, Mapping, np.ndarray, StructuredArray]] = None, **kwargs: Iterable):
        if isinstance(items, StructuredArray): self._arrs, self._length = items._arrs.copy(), items._length; return

        vals = [(k, items[k]) for k in items.dtype.names] if isinstance(items, np.ndarray) and available(items.dtype.names) else \
               items.items()  if ismapping(items) else \
               items          if iterable(items) else \
               kwargs.items() if missing(items) else None
        if missing(vals): raise TypeError('unknow data type')

        self._arrs = OrderedDict()
        self._length = None
        for k,v in vals: self[k] = v

    # privates
    def _parseids(self, idx, axis = None, mapslice = True):
        if missing(axis):
            sids, aids = (idx, slice(None)) if not isinstance(idx, tuple) else \
                         (idx[0], slice(None)) if len(idx) == 1 else idx
        else:
            if isinstance(idx, tuple): raise IndexError('too many dimensions for array')
            if axis not in (0, 1): raise IndexError('invalid axis value')
            sids, aids = (idx, slice(None)) if axis == 0 else (slice(None), idx)

        def _wrap(ids):
            if ids is None: return slice(None)
            if isinstance(ids, slice): return ids
            if not listable(ids): return [ids]
            return ids
        sids, aids = smap((sids, aids), _wrap)

        if (isinstance(sids, slice) and mapslice) or (listable(sids) and checkany(sids, lambda x: not isstring(x))): sids = self.names[sids]
        return sids, aids

    def _parsevals(self, value):
        if isinstance(value, StructuredArray): return [value._arrs[n].copy() for n in self._arrs.keys()]
        if not iterable(value): return value

        value = ll(value)
        if len(value) == 0 or not iterable(value[0]): return np.asarray(value)

        value = smap(value, lambda x: np.asarray(ll(x)))
        if not len(set(smap(value, len))) == 1: raise ValueError('input arrays not in the same size')
        return value

    # built-ins
    def __getitem__(self, item):
        return self.take(item, axis = None)

    def __setitem__(self, key, value):
        self.put(key, value, axis = None, inline = True)

    def __delitem__(self, key):
        self.delete(key, axis = None, inline = True)

    def __getattr__(self, item):
        return self._arrs[item] if item in self else super().__getattribute__(item)

    def __iter__(self):
        return iter(self._arrs.keys())

    def __contains__(self, item):
        return item in self._arrs

    def __len__(self):
        return self.size

    def __eq__(self, other):
        if isinstance(other, StructuredArray):
            equ = self.shape == other.shape and \
                  set(self._arrs.keys()) == set(other._arrs.keys()) and \
                  checkall(self._arrs.keys(), lambda k: np.all(self._arrs[k] == other._arrs[k]) if self._arrs[k].dtype.kind != 'f' else
                                                        np.allclose(self._arrs[k], other._arrs[k]))
        else:
            equ = np.asarray(self.arrays, dtype = object) == np.asarray(other, dtype = object)
        return equ

    def __str__(self):
        if len(self._arrs) == 0: return '[ ]'
        nlen = max(smap(self._arrs.keys(), len))
        olns = [(('{'+f':{nlen}s'+'} : ').format(k) if i == 0 else (' ' * (nlen + 3))) + ln
                for k,v in zip(self._arrs.keys(), smap(self._arrs.values(), str)) for i,ln in enumerate(v.split('\n'))]
        return paste(olns, sep = '\n')

    def __repr__(self):
        rlns = str(self).split('\n')
        rlns = ['StructuredArray(' + rlns[0]] + \
               ['                ' + ln for ln in rlns[1:]]
        return paste(rlns, sep = '\n') + f', size = ({self.size}, {self.length}))'

    # for numpy
    def __array__(self, dtype = None):
        if available(dtype): return np.asarray(self.arrays, dtype = dtype)
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
    def take(self, pos: Indices2D, axis: Optional[int] = 0) -> StructuredArray:
        if isstring(pos): return self._arrs[pos]
        sids, aids = self._parseids(pos, axis = axis)
        return StructuredArray([(k, self._arrs[k][aids]) for k in sids])

    def put(self, pos: Indices2D, value: Any, axis: Optional[int] = 0, inline: bool = False) -> StructuredArray:
        narr = self if inline else self.copy()
        vals = self._parsevals(value)

        if isstring(pos):
            if not isinstance(vals, np.ndarray): raise ValueError('input array not in 1-dimensional')
            if missing(narr._length): narr._length = vals.shape[0]
            elif narr._length != vals.shape[0]: raise ValueError('input array size not match')
            narr._arrs[pos] = vals.copy()
        else:
            sids, aids = self._parseids(pos, axis = axis)
            if not isinstance(vals, list):
                for k in sids: narr._arrs[k][aids] = vals
            else:
                if len(sids) != len(vals): raise ValueError('input names and values size not match')
                for k,vals in zip(sids, vals): narr._arrs[k][aids] = vals
        return narr

    def append(self, value: Any, inline: bool = False) -> StructuredArray:
        return self.insert(None, value = value, inline = inline)

    def insert(self, pos: Indices, value: Any, inline: bool = False) -> StructuredArray:
        narr = self if inline else self.copy()
        vals = self._parsevals(value)

        _upd = (lambda x,y: np.insert(x, pos, y)) if available(pos) else (lambda x,y: np.hstack([x, y]))
        if not isinstance(vals, list):
            for k, v in narr._arrs.items(): narr._arrs[k] = _upd(v, vals)
            narr._length += vals.shape[0] if isinstance(vals, np.ndarray) else 1
        else:
            if len(vals) != narr.size: raise ValueError('input values size not match')
            for (k,v), o in zip(narr._arrs.items(), vals): narr._arrs[k] = _upd(v, o)
            narr._length += vals[0].shape[0]
        return narr

    def delete(self, pos: Indices2D, axis: Optional[int] = 0, inline: bool = False) -> StructuredArray:
        narr = self if inline else self.copy()
        if isstring(pos): del narr._arrs[pos]; return narr

        sids, aids = self._parseids(pos, axis = axis, mapslice = False)
        slic = isinstance(sids, slice) and sids == slice(None)
        alic = isinstance(aids, slice) and aids == slice(None) and (missing(axis) or axis == 0)

        if slic and alic:
            narr._arrs = OrderedDict()
            narr._length = None
        elif slic and not alic:
            if listable(aids) and len(aids) == 1 and aids[0] < 0: aids = aids[0] # fix the issue that currently negative indices are ignored by np.delete
            for k,v in narr._arrs.items(): narr._arrs[k] = np.delete(v, aids)
            narr._length = len(narr._arrs[l(narr._arrs.keys())[0]])
        elif not slic and alic:
            if isinstance(sids, slice) or sids.dtype.kind not in ('S', 'U'): sids = narr.names[sids]
            for k in sids: del narr._arrs[k]
        else: raise IndexError('unable to delete portion of the array')

        return narr

    def tolist(self) -> List:
        return self.arrays

    def tostring(self) -> str:
        return str(self)

    def tomultindex(self) -> pd.MultiIndex:
        if self.size == 0: raise ValueError('unable to create MultiIndex from empty array')
        return pd.MultiIndex.from_arrays(self.arrays, names = self.names.tolist())

    def copy(self) -> StructuredArray:
        narr = StructuredArray()
        narr._arrs = OrderedDict([(k, v.copy()) for k,v in self._arrs.items()])
        narr._length = self._length
        return narr

    # file portals
    @classmethod
    def fromsarray(cls, array: np.ndarray) -> StructuredArray:
        _r = re.compile('<(.*)::([<>|]?[biufcmMOSUV]\\d*)>')
        nams, vals = array[:,0], array[:,1:]
        nams, vdts = np.vectorize(lambda x: (lambda v: v[0] if len(v) > 0 else '')(_r.findall(x)))(nams)
        vals = smap(zip(vals,vdts), unpack(lambda v,d: np.asarray(v).astype(d) if d != '|b1' else v == 'True'))
        return StructuredArray(zip(nams, vals))

    def tosarray(self, withdtype: bool = True) -> np.ndarray:
        vals = np.array([
            np.r_[[f'<{k}::{v.dtype.str}>' if withdtype else str(k)], v.astype(str)]
            for k,v in self._arrs.items()
        ])
        return vals

    @classmethod
    def loadcsv(cls, fname: Union[str, Path], delimiter: str = ',', transposed: bool = True) -> StructuredArray:
        idm = np.array(tablePortal.load(fname, delimiter = delimiter))
        if transposed: idm = idm.T
        return cls.fromsarray(idm)

    def savecsv(self, fname: Union[str, Path], delimiter: str = ',', transpose: bool = True) -> bool:
        odm = self.tosarray()
        if transpose: odm = odm.T
        return tablePortal.save(odm, fname, delimiter = delimiter)

    @classmethod
    def fromhtable(cls, hdftable: tb.Table) -> StructuredArray:
        nams = hdftable.attrs.names
        knds = hdftable.attrs.kinds
        vals = [np.array(hdftable.colinstances[n]).astype(t) for n,t in zip(nams,knds)]
        return StructuredArray(zip(nams, vals))

    def tohtable(self, root: tb.Group, tabname: str) -> tb.Table:
        desc = type('_struct_array', (tb.IsDescription,), {n: tb.Col.from_dtype(v.dtype) for n,v in self._arrs.items()})
        tabl = tb.Table(root, tabname, desc)
        tabl.append([self._arrs[n] for n in tabl.colnames]) # desc.columns is an un-ordered dict
        tabl.attrs.names = self.names
        tabl.attrs.kinds = [v.dtype.str for v in self.arrays]
        return tabl

    @classmethod
    def loadhdf(cls, fname: Union[str, Path]) -> StructuredArray:
        checkInputFile(fname)
        with tb.open_file(fname, mode = 'r') as hdf: arr = cls.fromhtable(hdf.root.StructuredArray)
        return arr

    def savehdf(self, fname: Union[str, Path], compression: int = 0) -> bool:
        checkOutputFile(fname)
        with tb.open_file(fname, mode = 'w', filters = tb.Filters(compression)) as hdf: self.tohtable(hdf.root, 'StructuredArray')
        return os.path.isfile(fname)
