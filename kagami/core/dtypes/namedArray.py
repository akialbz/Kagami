#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
namedArray

author(s): Albert (aki) Zhou
origin: 02-18-2017

"""


import os, tables
import cPickle as cp
import numpy as np
from copy import deepcopy
from string import join
from kagami.core.prelim import NA, optional, isna, listable, checkany
from kagami.core.filesys import checkInputFile, checkOutputFile


class NamedArray(object):
    def __init__(self, X, dtype = float, rownames = NA, colnames = NA, metadata = NA, strfmt = 'S32'):
        self._dmatx = np.array(X).astype(dtype)
        self._dtype = dtype
        self._metas = {} if isna(metadata) else dict(metadata)
        self._sfmt = strfmt
        if self._dmatx.dtype.kind in ('S','U'): self._dmatx, self._dtype = self._dmatx.astype(strfmt), strfmt

        self._rname, self._cname = None, None
        self._rndct, self._cndct = None, None
        self.rownames = rownames
        self.colnames = colnames

    # privates
    def _parseKey(self, key):
        rids, cids = (key, slice(None)) if not isinstance(key, tuple) else \
                     (key[0], slice(None)) if len(key) == 1 else key

        def _map(ids, axis):
            if not listable(ids): ids = [ids]
            if len(ids) == 0: return []
            ids = ids if isinstance(ids[0], int) else \
                  np.where(ids)[0] if isinstance(ids[0] ,(bool, np.bool_)) else \
                  self.mapNames(ids, axis)
            return ids
        rids = np.arange(self.nrow)[rids] if isinstance(rids, slice) else _map(rids, 0)
        cids = np.arange(self.ncol)[cids] if isinstance(cids, slice) else _map(cids, 1)

        return rids, cids

    def _newRowArray(self, other, dmtx, rnams):
        if self.ncol != other.ncol: raise ValueError('array have different column numbers')
        if not np.all(self.colnames == other.colnames): raise ValueError('array have different column names')
        return NamedArray(dmtx, dtype = self.dtype, strfmt = self._sfmt,
                          rownames = rnams, colnames = self.colnames)

    def _newColArray(self, other, dmtx, cnams):
        if self.nrow != other.nrow: raise ValueError('array have different row numbers')
        if not np.all(self.rownames == other.rownames): raise ValueError('arrays have different row names')
        return NamedArray(dmtx, dtype = self.dtype, strfmt = self._sfmt,
                          rownames = self.rownames, colnames = cnams)

    # built-ins
    def __getitem__(self, item):
        rids, cids = self._parseKey(item)
        return NamedArray(self._dmatx[np.ix_(rids,cids)], dtype = self.dtype, strfmt = self._sfmt,
                          rownames = self.rownames[rids], colnames = self.colnames[cids])

    def __setitem__(self, key, value):
        rids, cids = self._parseKey(key)
        if isinstance(value, NamedArray): value = value.values
        self._dmatx[np.ix_(rids,cids)] = value

    def __add__(self, other):
        return self.stack(other, axis = 0)

    def __len__(self):
        return self.nrow

    def __str__(self):
        s = self.toStr(delimiter = '\t') + '\n' + \
            '[%s]: %d x %d' % (str(self.dtype), self.nrow, self.ncol)
        return s

    def __repr__(self):
        return str(self)

    def __array__(self):
        return self.values # for np.array conversion

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
        self._rndct = {n:i for i,n in enumerate(self.rownames)}

    @property
    def colnames(self):
        return self._cname

    @colnames.setter
    def colnames(self, value):
        self._cname = np.arange(self.ncol) if isna(value) or value is None else np.array(value)
        if self._cname.dtype.kind in ('S', 'U'): self._cname = self._cname.astype(self._sfmt)
        if len(self._cname) != self.ncol: raise ValueError('column names and data matrix size not match')
        if len(self._cname) != len(np.unique(self._cname)): raise ValueError('column names have duplications')
        self._cndct = {n:i for i,n in enumerate(self.colnames)}

    @property
    def T(self):
        return NamedArray(self.values.T, dtype = self.dtype, strfmt = self._sfmt,
                          rownames = self.colnames, colnames = self.rownames)

    @property
    def metadata(self):
        return self._metas

    # publics
    def mapNames(self, names, axis = 0):
        if axis not in (0, 1): raise IndexError('unsupported axis %d' % axis)
        nd = self._rndct if axis == 0 else self._cndct
        idx = np.array([nd.get(n, None) for n in names])
        if None in idx: raise KeyError('name(s) not found')
        return idx

    def stack(self, other, axis = 0):
        if axis == 0:
            return self._newRowArray(other, np.vstack((self.values, other.values)),
                                     rnams = np.hstack((self.rownames, other.rownames)))
        elif axis == 1:
            return self._newColArray(other, np.hstack((self.values, other.values)),
                                     cnams = np.hstack((self.colnames, other.colnames)))
        else: raise IndexError('unsupported axis %d' % axis)

    def insert(self, other, ids = NA, axis = 0):
        if axis == 0:
            ids = optional(ids, self.nrow)
            return self._newRowArray(other, np.insert(self.values, ids, other.values, axis == 0),
                                     rnams = np.insert(self.rownames, ids, other.rownames))
        elif axis == 1:
            ids = optional(ids, self.ncol)
            return self._newColArray(other, np.insert(self.values, ids, other.values, axis == 1),
                                     cnams = np.insert(self.colnames, ids, other.colnames))
        else: raise IndexError('unsupported axis %d' % axis)

    def drop(self, ids, axis = 0):
        if axis == 0:
            return NamedArray(np.delete(self.values, ids, axis = 0), dtype = self.dtype, strfmt = self._sfmt,
                              rownames = np.delete(self.rownames, ids), colnames = self.colnames)
        elif axis == 1:
            return NamedArray(np.delete(self.values, ids, axis = 1), dtype = self.dtype, strfmt = self._sfmt,
                              rownames = self.rownames, colnames = np.delete(self.colnames, ids))
        else: raise IndexError('unsupported axis %d' % axis)

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

    def toFile(self, fname):
        checkOutputFile(fname)
        with open(fname, 'w') as f: cp.dump(self, f, protocol = cp.HIGHEST_PROTOCOL)
        return os.path.isfile(fname)


