#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
namedIndex

author(s): Albert (aki) Zhou
origin: 08-23-2018

"""


from __future__ import annotations

import numpy as np
from typing import List, Iterable, Union, Any
from kagami.common import optional, missing, isstring, iterable, listable, checkany, paste
from .coreType import CoreType


__all__ = ['NamedIndex']


Indices = Union[int, str, Iterable[Union[int, bool, str]], slice]

class NamedIndex(CoreType):
    __slots__ = ('_names', '_nidct')

    def __init__(self, names: Iterable[str] = ()):
        self.names = names

    # private
    def _reindex(self, check = True):
        self._nidct = {n: i for i, n in enumerate(self._names)}  # much faster than dict()
        if check and len(self._names) != len(self._nidct): raise KeyError('index names not unique')

    def _parseIds(self, ids):
        if (iterable(ids) and checkany(ids, isstring)) or isstring(ids): ids = self.idsof(ids, safe = False)
        if isinstance(ids, tuple): ids = list(ids)
        return ids

    @staticmethod
    def _parseVals(value, arrayOnly = False):
        if isinstance(value, NamedIndex):
            val = value.names
        elif not iterable(value):
            if arrayOnly: raise TypeError('index names must be an array')
            if not isstring(value): raise TypeError('index name must be a string')
            val = value
        else:
            if checkany(value, lambda x: not isstring(x)): raise TypeError('index names must be strings')
            if not listable(value): value = list(value)
            val = np.array(value, dtype = object)
        return val

    # built-ins
    def __getitem__(self, item):
        return self.take(item)

    def __setitem__(self, key, value):
        self.put(key, value)

    def __delitem__(self, key):
        self._names = np.delete(self._names, key)
        self._reindex(check = False)

    def __iter__(self):
        return iter(self._names)

    def __contains__(self, item):
        return item in self._names

    def __len__(self):
        return self.size

    def __eq__(self, other):
        if not listable(other): other = list(other)
        return self._names == other

    def __str__(self):
        return str(self._names)

    def __repr__(self):
        rlns = str(self._names).split('\n')
        rlns = [f'NamedIndex({rlns[0]}'] + \
               [f'           {ln}' for ln in rlns[1:]]
        return paste(*rlns, sep = '\n') + f', size = {self.size})'

    # for numpy
    def __array__(self, dtype = None):
        return self._names.astype(optional(dtype, str))

    def __array_wrap__(self, arr):
        return NamedIndex(arr)

    # properties
    @property
    def names(self) -> np.ndarray:
        return self._names.copy() # DO NOT use _names[:] -> does not make deep copy for obj array

    @names.setter
    def names(self, value: Iterable[str]) -> None:
        if isinstance(value, NamedIndex):
            self._names, self._nidct = value._names.copy(), value._nidct.copy(); return
        self._names = self._parseVals(value, arrayOnly = True)
        self._reindex()

    @property
    def size(self) -> int:
        return self._names.size

    @property
    def shape(self) -> tuple:
        return self._names.shape

    @property
    def ndim(self) -> int:
        return 1

    # public
    @staticmethod
    def uniqueRenaming(names: Iterable[str], suffix: str = '.{}') -> np.ndarray:
        names = NamedIndex._parseVals(names, arrayOnly = True)

        unam, cnts = np.unique(names, return_counts = True)
        if np.all(cnts == 1): return names

        cdct = {n:c for n,c in zip(unam, cnts-1)}
        for i,n in enumerate(names[::-1]):
            c = cdct[n]
            if c > 0: names[-i-1], cdct[n] = n + suffix.format(i), c - 1
        return names

    def namesof(self, ids: Union[int, Sequence[int]]) -> Union[str, np.ndarray]:
        return self._names[self._parseIds(ids)]

    def idsof(self, names: Union[str, Iterable[str]], safe: bool = False) -> Union[None, int, List]:
        if isstring(names):
            ids = self._nidct.get(names, None)
            if not safe and missing(ids): raise KeyError(f'unknown index name {names}')
        else:
            ids = [self._nidct.get(n, None) for n in names]
            if not safe and checkany(ids, missing): raise KeyError('unknown index name(s)')
        return ids

    def take(self, pos: Indices) -> Union[str, NamedIndex]:
        pos = self._parseIds(pos)
        return self._names[pos] if isinstance(pos, int) else NamedIndex(self._names[pos])

    def put(self, pos: Indices, value: Union[str, Iterable[str]]) -> NamedIndex:
        pos = self._parseIds(pos)
        val = self._parseVals(value)
        if isinstance(pos, int):
            if not isstring(val): raise TypeError('cannot assign multiple names to one position')
            self._nidct.pop(self._names[pos])
            if val in self._nidct: raise KeyError('index names not unique')
            self._names[pos], self._nidct[val] = val, pos
        else:
            self._names[pos] = val
            self._reindex()
        return self

    def append(self, value: [str, Iterable[str]], inline: bool = False) -> NamedIndex:
        val = self._parseVals(value)
        nid = self if inline else self.copy()
        nid._names = np.hstack([nid._names, val])
        for i,n in enumerate(val): nid._nidct[n] = nid.size + i
        if len(nid._names) != len(nid._nidct): raise KeyError('index names not unique')
        return nid

    def insert(self, pos: Indices, values: [str, Iterable[str]], inline: bool = False) -> NamedIndex:
        pos = self._parseVals(pos)
        val = self._parseVals(values)
        nid = self if inline else self.copy()
        nid._names = np.insert(nid._names, pos, val)
        nid._reindex()
        return nid

    def delete(self, pos: Indices, inline: bool = False) -> NamedIndex:
        pos = self._parseIds(pos)
        nid = self if inline else self.copy()
        nid._names = np.delete(self._names, pos)
        nid._reindex(check = False)
        return nid

    def tolist(self) -> Any:
        return self._names.tolist()

    def tostring(self) -> bytes:
        return self._names.tostring()

    def sort(self, kind = 'quicksort', inline: bool = False) -> NamedIndex:
        nid = self if inline else self.copy()
        sids = np.argsort(nid._names, kind = kind)
        nid._nidct = {n:i for n,i in zip(nid._names, sids)}
        nid._names = nid._names[sids]
        return nid

    def argsort(self, kind = 'quicksort') -> np.ndarray:
        return np.argsort(self._names, kind = kind)

    def copy(self) -> NamedIndex:
        nid = NamedIndex()
        nid._names = self._names.copy()
        nid._nidct = self._nidct.copy()
        return nid
