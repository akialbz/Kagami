#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
dataset: the Dataset class

author(s): Albert (aki) Zhou
origin: 02-18-2017

"""


import numpy as np
from copy import deepcopy
from itertools import product
from string import join
from ..prelim import NA, optional, isna, listable, checkany
from index import _Index


# Dataset class
class Dataset(object):
    def __init__(self, X, dtype = float, rownames = NA, colnames = NA, rowindex = NA, colindex = NA, strfmt = 'S32'):
        self._dmatx = np.array(X).astype(dtype)
        self._dtype = dtype
        self._sfmt = strfmt
        if self._dmatx.dtype.kind in ('S','U'): self._dmatx, self._dtype = self._dmatx.astype(strfmt), strfmt

        self._rname, self._cname = None, None
        self.rownames = rownames
        self.colnames = colnames

        self._rindx, self._cindx = None, None
        self.rowindex = rowindex
        self.colindex = colindex

    # privates
    def _parseKey(self, key):
        rids, cids = (key, slice(None)) if not isinstance(key, tuple) else \
                     (key[0], slice(None)) if len(key) == 1 else key

        def _map(ids, nas):
            if not listable(ids): ids = [ids]
            ids = ids if isinstance(ids[0], int) else \
                  np.where(ids)[0] if isinstance(ids[0] ,(bool, np.bool_)) else \
                  np.where(np.logical_or.reduce(map(lambda x: nas == x, ids)))[0]
            return ids
        rids = rids if isinstance(rids, slice) else _map(rids, self.rownames)
        cids = cids if isinstance(cids, slice) else _map(cids, self.colnames)

        return rids, cids

    def _newRowDS(self, other, dmtx, rnams, rindx):
        if self.ncol != other.ncol: raise ValueError('datasets have different column numbers')
        if not np.all(self.colnames == other.colnames): raise ValueError('datasets have different column names')
        if not self.colindex == other.colindex: raise ValueError('datasets have different column indices')
        return Dataset(dmtx, dtype = self.dtype, strfmt = self._sfmt,
                       rownames = rnams, colnames = self.colnames,
                       rowindex = rindx, colindex = self.colindex)

    def _newColDS(self, other, dmtx, cnams, cindx):
        if self.nrow != other.nrow: raise ValueError('datasets have different row numbers')
        if not np.all(self.rownames == other.rownames): raise ValueError('datasets have different row names')
        if not self.rowindex == other.rowindex: raise ValueError('datasets have different row indices')
        return Dataset(dmtx, dtype = self.dtype, strfmt = self._sfmt,
                       rownames = self.rownames, colnames = cnams,
                       rowindex = self.rowindex, colindex = cindx)

    # built-ins
    def __getitem__(self, item):
        rids, cids = self._parseKey(item)
        return Dataset(self._dmatx[rids, cids], dtype = self.dtype, strfmt = self._sfmt,
                       rownames = self.rownames[rids], colnames = self.colnames[cids],
                       rowindex = self.rowindex[:,rids], colindex = self.colindex[:,cids])

    def __setitem__(self, key, value):
        rids, cids = self._parseKey(key)
        self._dmatx[rids, cids] = value

    def __add__(self, other):
        return self.stack(other, axis = 1)

    def __len__(self):
        return self.nrow

    def __str__(self):
        return self.toStr(delimiter = '\t')

    def __repr__(self):
        return self.toStr(delimiter = '\t')

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

    @dtype.setter
    def dtype(self, value):
        self._dmatx = self._dmatx.astype(value)
        self._dtype = value
        if self._dmatx.dtype.kind in ('S','U'): self._dmatx, self._dtype = self._dmatx.astype(self._sfmt), self._sfmt

    @property
    def nrow(self):
        return self.shape[0]

    @property
    def ncol(self):
        return self.shape[1]

    @property
    def shape(self):
        return self.values.shape

    @property
    def rownames(self):
        return self._rname

    @rownames.setter
    def rownames(self, value):
        self._rname = np.arange(self.nrow) if isna(value) or value is None else np.array(value)
        if self._rname.dtype.kind in ('S', 'U'): self._rname = self._rname.astype(self._sfmt)
        if len(self._rname) != self.nrow: raise ValueError('row names and data matrix size not match')
        if len(self._rname) != len(np.unique(self._rname)): raise ValueError('row names have duplications')

    @property
    def colnames(self):
        return self._cname

    @colnames.setter
    def colnames(self, value):
        self._cname = np.arange(self.ncol) if isna(value) or value is None else np.array(value)
        if self._cname.dtype.kind in ('S', 'U'): self._cname = self._cname.astype(self._sfmt)
        if len(self._cname) != self.ncol: raise ValueError('column names and data matrix size not match')
        if len(self._cname) != len(np.unique(self._cname)): raise ValueError('column names have duplications')

    @property
    def rowindex(self):
        return self._rindx

    @rowindex.setter
    def rowindex(self, value):
        self._rindx = _Index(value)
        if self._rindx.ndim != self.nrow: raise ValueError('row index and data matrix size not match')

    @property
    def colindex(self):
        return self._cindx

    @colindex.setter
    def colindex(self, value):
        self._cindx = _Index(value)
        if self._cindx.ndim != self.ncol: raise ValueError('column index and data matrix size not match')

    @property
    def T(self):
        return Dataset(self.values.T, dtype = self.dtype, strfmt = self._sfmt,
                       rownames = self.colnames, colnames = self.rownames,
                       rowindex = self.colindex, colindex = self.rowindex)

    # publics
    def stack(self, other, axis = 0):
        if axis == 0:
            return self._newRowDS(other, np.vstack((self.values, other.values)),
                                  rnams = np.hstack((self.rownames, other.rownames)),
                                  rindx = self.rowindex + other.rowindex)
        elif axis == 1:
            return self._newColDS(other, np.hstack((self.values, other.values)),
                                  cnams = np.hstack((self.colnames, other.colnames)),
                                  cindx = self.colindex + other.colindex)
        else: raise IndexError('unsupported axis %d' % axis)

    def insert(self, other, ids = NA, axis = 0):
        if axis == 0:
            ids = optional(ids, self.nrow)
            return self._newRowDS(other, np.insert(self.values, ids, other.values, axis == 0),
                                  rnams = np.insert(self.rownames, ids, other.rownames),
                                  rindx = self.rowindex.insert(other, ids))
        elif axis == 1:
            ids = optional(ids, self.ncol)
            return self._newColDS(other, np.insert(self.values, ids, other.values, axis == 1),
                                  cnams = np.insert(self.colnames, ids, other.colnames),
                                  cindx = self.colindex.insert(other, ids))
        else: raise IndexError('unsupported axis %d' % axis)

    def drop(self, ids, axis = 0):
        if axis == 0:
            return Dataset(np.delete(self.values, ids, axis = 0), dtype = self.dtype, strfmt = self._sfmt,
                           rownames = np.delete(self.rownames, ids), colnames = self.colnames,
                           rowindex = self.rowindex.drop(ids, axis = 1), colindex = self.colindex)
        elif axis == 1:
            return Dataset(np.delete(self.values, ids, axis = 1), dtype = self.dtype, strfmt = self._sfmt,
                           rownames = self.rownames, colnames = np.delete(self.colnames, ids),
                           rowindex = self.rowindex, colindex = self.colindex.drop(ids, axis = 1))
        else: raise IndexError('unsupported axis %d' % axis)

    def group(self, names, groupName, axis = 0, asStr = False):
        def _group(indx):
            if checkany(names, lambda x: x not in indx): raise KeyError('index name(s) not exists')
            if groupName in indx: raise KeyError('group name [%s] already exists' % groupName)
            ivals = indx[names,].indices
            combs = product(*map(np.unique, ivals))
            cdct = {tuple(c): (join(map(str,c), '_') if asStr else i) for i,c in enumerate(combs)}
            return [cdct[tuple(c)] for c in zip(*ivals)]

        if axis == 0: self.rowindex[groupName] = _group(self.rowindex)
        elif axis == 1: self.colindex[groupName] = _group(self.colindex)
        else: raise IndexError('unsupported axis %d' % axis)
        return self

    def astype(self, dtype):
        ds = self.copy()
        ds.dtype = dtype
        return ds

    def copy(self):
        return deepcopy(self)

    def toList(self, transpose = False):
        return list(map(list, (self.values.T if transpose else self.values)))

    def toStr(self, delimiter = ',', transpose = False):
        rn, cn = (self.rownames, self.colnames) if not transpose else (self.colnames, self.rownames)
        omtx = [[' '] + list(cn)] + \
               [[n] + list(l) for n,l in zip(rn, self.toList(transpose))]
        return join([join(map(str,ln), delimiter) for ln in omtx], '\n')

