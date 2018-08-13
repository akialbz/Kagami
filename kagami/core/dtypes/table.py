#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
table

author(s): Albert (aki) Zhou
origin: 02-18-2017

"""


import os, tables
import cPickle as cp
import numpy as np
from collections import OrderedDict
from copy import deepcopy
from string import join
from kagami.core.prelim import NA, optional, isna, hasvalue, listable, hashable, checkany
from kagami.core.filesys import checkInputFile, checkOutputFile


# table index class
class _Index(dict):
    def __init__(self, seq = NA, ndim = NA, **kwargs):
        super(_Index, self).__init__(optional(seq, None), **kwargs)
        if hasvalue(ndim): self._ndim = ndim
        elif len(self) > 0: self._ndim = len(self.values()[0])
        else: raise ValueError('must provide index size or initial values')
        if checkany(self.values(), lambda x: len(x) != ndim): raise ValueError('index values size not match')

    # build-ins
    def __getitem__(self, item):
        if hashable(item) and self.has_key(item): return super(_Index, self).__getitem__(item)
        return _Index([(k,v[item]) for k,v in self.items()])

    def __setitem__(self, key, value):
        if len(value) != self._ndim: raise ValueError('index values size not match')
        super(_Index, self).__setitem__(key, value)

    # properties
    @property
    def ndim(self):
        return self._ndim

    @property
    def shape(self):
        return len(self), self._ndim

    # publics
    def insert(self, other, ids = NA):
        if not isinstance(other, _Index): raise TypeError('insert object is not Index')
        if set(self.keys()) != set(other.keys()): raise KeyError('indices have different keys')
        pos = optional(ids, self._ndim)
        return _Index([(k, np.insert(v, pos, other[k])) for k,v in self.items()])

    def drop(self, ids = NA):
        pos = optional(ids, self._ndim)
        return _Index([(k, np.delete(v,pos)) for k,v in self.items()])


# table class
class Table(object):
    def __init__(self, X, dtype = float, rownames = NA, colnames = NA, rowindex = NA, colindex = NA, metadata = NA):
        self._dmatx = np.array(X).astype(dtype)
        self._dtype = dtype
        self._metas = {} if isna(metadata) else dict(metadata)

        self._rndct = None
        self.rownames = rownames
        self._cndct = None
        self.colnames = colnames

        self._rindx = None
        self.rowindex = rowindex
        self._cindx = None
        self.colindex = colindex

    # properties
    @property
    def values(self):
        return self._dmatx

    @values.setter
    def values(self, value):
        self._dmatx[:] = np.array(value, dtype = self.dtype)

    @property
    def dtype(self):
        return self._dtype

    @property
    def nrow(self):
        return self.shape[0]

    @property
    def ncol(self):
        return self.shape[1]

    @property
    def shape(self):
        return self._dmatx.shape

    @property
    def rownames(self):
        return np.array(self._rndct.keys())

    @rownames.setter
    def rownames(self, value):
        if isna(value) or value is None:
            value = map(lambda x: 'R.%d' % x, np.arange(self.nrow))
        else:
            if len(value) != self.nrow: raise ValueError('row names and data matrix size not match')
            if len(value) != len(set(value)): raise ValueError('row names have duplications')
        self._rndct = OrderedDict([(n,i) for i,n in enumerate(value)])

    @property
    def colnames(self):
        return np.array(self._cndct.keys())

    @colnames.setter
    def colnames(self, value):
        if isna(value) or value is None:
            value = map(lambda x: 'C.%d' % x, np.arange(self.ncol))
        else:
            if len(value) != self.ncol: raise ValueError('column names and data matrix size not match')
            if len(value) != len(set(value)): raise ValueError('column names have duplications')
        self._cndct = OrderedDict([(n,i) for i,n in enumerate(value)])

    @property
    def rowindex(self):
        return self._rindx

    @rowindex.setter
    def rowindex(self, value):
        self._rindx = _Index(value, ndim = self.nrow)

    @property
    def colindex(self):
        return self._cindx

    @colindex.setter
    def colindex(self, value):
        self._cindx = _Index(value, ndim = self.ncol)

    @property
    def metadata(self):
        return self._metas

    @property
    def T(self):
        arr = deepcopy(self)
        arr._dmatx = arr._dmatx.T
        arr._rndct, arr._cndct = arr._cndct, arr._rndct
        return arr







# class _old():
#     # privates
#     def _parseKey(self, key):
#         rids, cids = (key, slice(None)) if not isinstance(key, tuple) else \
#                      (key[0], slice(None)) if len(key) == 1 else key
#
#         def _map(ids, axis):
#             if not listable(ids): ids = [ids]
#             if len(ids) == 0: return []
#             ids = ids if isinstance(ids[0], int) else \
#                   np.where(ids)[0] if isinstance(ids[0] ,(bool, np.bool_)) else \
#                   self.mapNames(ids, axis)
#             return ids
#         rids = np.arange(self.nrow)[rids] if isinstance(rids, slice) else _map(rids, 0)
#         cids = np.arange(self.ncol)[cids] if isinstance(cids, slice) else _map(cids, 1)
#
#         return rids, cids
#
#     def _newRowArray(self, other, dmtx, rnams):
#         if self.ncol != other.ncol: raise ValueError('array have different column numbers')
#         if not np.all(self.colnames == other.colnames): raise ValueError('array have different column names')
#         return NamedArray(dmtx, dtype = self.dtype, strfmt = self._sfmt,
#                           rownames = rnams, colnames = self.colnames)
#
#     def _newColArray(self, other, dmtx, cnams):
#         if self.nrow != other.nrow: raise ValueError('array have different row numbers')
#         if not np.all(self.rownames == other.rownames): raise ValueError('arrays have different row names')
#         return NamedArray(dmtx, dtype = self.dtype, strfmt = self._sfmt,
#                           rownames = self.rownames, colnames = cnams)
#
#     # built-ins
#     def __getitem__(self, item):
#         rids, cids = self._parseKey(item)
#         return NamedArray(self._dmatx[np.ix_(rids,cids)], dtype = self.dtype, strfmt = self._sfmt,
#                           rownames = self.rownames[rids], colnames = self.colnames[cids])
#
#     def __setitem__(self, key, value):
#         rids, cids = self._parseKey(key)
#         if isinstance(value, NamedArray): value = value.values
#         self._dmatx[np.ix_(rids,cids)] = value
#
#     def __add__(self, other):
#         return self.stack(other, axis = 0)
#
#     def __len__(self):
#         return self.nrow
#
#     def __str__(self):
#         s = self.toStr(delimiter = '\t') + '\n' + \
#             '[%s]: %d x %d' % (str(self.dtype), self.nrow, self.ncol)
#         return s
#
#     def __repr__(self):
#         return str(self)
#
#     def __array__(self):
#         return self.values # for np.array conversion
#
#     # publics
#     def mapNames(self, names, axis = 0):
#         if axis not in (0, 1): raise IndexError('unsupported axis %d' % axis)
#         nd = self._rndct if axis == 0 else self._cndct
#         idx = np.array([nd.get(n, None) for n in names])
#         if None in idx: raise KeyError('name(s) not found')
#         return idx
#
#     def stack(self, other, axis = 0):
#         if axis == 0:
#             return self._newRowArray(other, np.vstack((self.values, other.values)),
#                                      rnams = np.hstack((self.rownames, other.rownames)))
#         elif axis == 1:
#             return self._newColArray(other, np.hstack((self.values, other.values)),
#                                      cnams = np.hstack((self.colnames, other.colnames)))
#         else: raise IndexError('unsupported axis %d' % axis)
#
#     def insert(self, other, ids = NA, axis = 0):
#         if axis == 0:
#             ids = optional(ids, self.nrow)
#             return self._newRowArray(other, np.insert(self.values, ids, other.values, axis == 0),
#                                      rnams = np.insert(self.rownames, ids, other.rownames))
#         elif axis == 1:
#             ids = optional(ids, self.ncol)
#             return self._newColArray(other, np.insert(self.values, ids, other.values, axis == 1),
#                                      cnams = np.insert(self.colnames, ids, other.colnames))
#         else: raise IndexError('unsupported axis %d' % axis)
#
#     def drop(self, ids, axis = 0):
#         if axis == 0:
#             return NamedArray(np.delete(self.values, ids, axis = 0), dtype = self.dtype, strfmt = self._sfmt,
#                               rownames = np.delete(self.rownames, ids), colnames = self.colnames)
#         elif axis == 1:
#             return NamedArray(np.delete(self.values, ids, axis = 1), dtype = self.dtype, strfmt = self._sfmt,
#                               rownames = self.rownames, colnames = np.delete(self.colnames, ids))
#         else: raise IndexError('unsupported axis %d' % axis)
#
#     def astype(self, dtype):
#         ds = self.copy()
#         ds.dtype = dtype
#         return ds
#
#     def copy(self):
#         return deepcopy(self)
#
#     def toList(self, transpose = False):
#         return list(map(list, (self.values.T if transpose else self.values)))
#
#     def toStr(self, delimiter = ',', transpose = False):
#         rn, cn = (self.rownames, self.colnames) if not transpose else (self.colnames, self.rownames)
#         omtx = [[' '] + list(cn)] + \
#                [[n] + list(l) for n,l in zip(rn, self.toList(transpose))]
#         return join([join(map(str,ln), delimiter) for ln in omtx], '\n')
#
#     def toFile(self, fname):
#         checkOutputFile(fname)
#         with open(fname, 'w') as f: cp.dump(self, f, protocol = cp.HIGHEST_PROTOCOL)
#         return os.path.isfile(fname)


