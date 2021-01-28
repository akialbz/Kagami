#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
namedIndex

author(s): Albert (aki) Zhou
added: 08-23-2018

"""


from __future__ import annotations

import numpy as np
from typing import List, Tuple, Iterable, Union
from kagami.comm import l, ll, optional, missing, isstring, iterable, listable, checkany, paste
from .coreType import CoreType, Indices


__all__ = ['NamedIndex']


class NamedIndex(CoreType):
    __slots__ = ('_names', '_nidct')

    def __init__(self, names: Iterable[str] = ()):
        self._names = self._nidct = None
        self.names = names

    # private
    def _reindex(self, check = True):
        self._nidct = {n: i for i,n in enumerate(self._names)}  # much faster than dict()
        if check and len(self._names) != len(self._nidct): raise KeyError('index names not unique')

    def _parseids(self, ids):
        if isinstance(ids, tuple): raise IndexError('too many dimensions for array')
        if (listable(ids) and checkany(ids, isstring)) or isstring(ids): return self.idsof(ids, safe = False)
        if listable(ids) and checkany(ids, lambda v: isinstance(v, bool)): return np.where(ids)[0]
        if ids is None: return slice(None)
        return ids

    @staticmethod
    def _parsevals(value, arrayonly = False):
        if isinstance(value, NamedIndex):
            val = value._names
        elif iterable(value):
            val = np.asarray(ll(value), dtype = object)
            if checkany(val, lambda x: not isstring(x)): raise TypeError('index names must be string')
        else:
            if arrayonly: raise TypeError('index names must be an array')
            if not isstring(value): raise TypeError('index name must be a string')
            val = value
        return val

    # built-ins
    def __getitem__(self, item):
        return self.take(item)

    def __setitem__(self, key, value):
        self.put(key, value, inline = True)

    def __delitem__(self, key):
        self.delete(key, inline = True)

    def __getattr__(self, item):
        return self._nidct[item] if item in self else super().__getattribute__(item)

    def __iter__(self):
        return iter(self._names)

    def __contains__(self, item):
        return item in self._names

    def __len__(self):
        return self.size

    def __eq__(self, other):
        if isinstance(other, NamedIndex): other = other._names
        return self._names == other

    def __str__(self):
        return str(self._names)

    def __repr__(self):
        rlns = str(self._names).split('\n')
        rlns = [f'NamedIndex({rlns[0]}'] + \
               [f'           {ln}' for ln in rlns[1:]]
        return paste(rlns, sep = '\n') + f', size = {self.size})'

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
            self._names, self._nidct = value._names.copy(), value._nidct.copy()
        else:
            self._names = self._parsevals(value, arrayonly = True).copy()
            self._reindex()

    @property
    def size(self) -> int:
        return self._names.shape[0]

    @property
    def shape(self) -> Tuple[int]:
        return self._names.shape

    @property
    def ndim(self) -> int:
        return 1

    # public
    @staticmethod
    def uniquenames(names: Iterable[str], suffix: str = '.{}') -> np.ndarray:
        names = NamedIndex._parsevals(names, arrayonly = True)

        unam, cnts = np.unique(names, return_counts = True)
        if np.all(cnts == 1): return names

        cdct = {n:c for n,c in zip(unam, cnts-1)}
        for i,n in enumerate(names[::-1]):
            c = cdct[n]
            if c > 0: names[-i-1], cdct[n] = n + suffix.format(c), c - 1
        return names

    def namesof(self, pos: Indices) -> Union[str, np.ndarray]:
        return self._names[self._parseids(pos)]

    def idsof(self, names: Union[str, Iterable[str]], safe: bool = False) -> Union[None, int, List[Union[None, int]]]:
        if isstring(names):
            ids = self._nidct.get(names, None)
            if not safe and missing(ids): raise KeyError(f'unknown index name {names}')
        else:
            ids = [self._nidct.get(n, None) if isstring(n) else n for n in names]
            if not safe and checkany(ids, missing): raise KeyError('unknown index name(s)')
        return ids

    def take(self, pos: Indices) -> Union[str, NamedIndex]:
        pos = self._parseids(pos)
        return self._names[pos] if isinstance(pos, int) else NamedIndex(self._names[pos])

    def put(self, pos: Indices, value: Union[str, Iterable[str]], inline: bool = False) -> NamedIndex:
        pos = self._parseids(pos)
        val = self._parsevals(value)
        nid = self if inline else self.copy()
        if isinstance(pos, int):
            if not isstring(val): raise TypeError('cannot assign multiple names to one position')
            nid._nidct.pop(nid._names[pos])
            if val in nid._nidct: raise KeyError('index names not unique')
            nid._names[pos], nid._nidct[val] = val, pos
        else:
            nid._names[pos] = val
            nid._reindex()
        return nid

    def append(self, value: Union[str, Iterable[str]], inline: bool = False) -> NamedIndex:
        val = self._parsevals(value)
        if not listable(val): val = [val]

        nid = self if inline else self.copy()
        for i,n in enumerate(val): nid._nidct[n] = nid.size + i
        nid._names = np.hstack([nid._names, val])

        if len(nid._names) != len(nid._nidct): raise KeyError('index names not unique')
        return nid

    def insert(self, pos: Indices, value: Union[str, Iterable[str]], inline: bool = False) -> NamedIndex:
        if missing(pos): return self.append(value, inline)
        pos = self._parseids(pos)
        val = self._parsevals(value)
        nid = self if inline else self.copy()
        nid._names = np.insert(nid._names, pos, val)
        nid._reindex()
        return nid

    def delete(self, pos: Indices, inline: bool = False) -> NamedIndex:
        pos = self._parseids(pos)
        nid = self if inline else self.copy()
        nid._names = np.delete(self._names, pos)
        nid._reindex(check = False)
        return nid

    def tolist(self) -> List:
        return l(self._names.tolist())

    def tostring(self) -> bytes:
        return self._names.tobytes()

    def copy(self) -> NamedIndex:
        nid = NamedIndex()
        nid._names = self._names.copy()
        nid._nidct = self._nidct.copy()
        return nid
