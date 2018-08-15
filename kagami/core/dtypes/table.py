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
from string import join
from kagami.core.prelim import NA, optional, isna, hasvalue, listable, hashable, checkany
from kagami.core.functional import partial
from kagami.core.filesys import checkInputFile, checkOutputFile


# table index class
class _Index(dict):
    def __init__(self, seq = NA, ndim = NA, **kwargs):
        if hasvalue(seq):
            super(_Index, self).__init__(seq)
        else:
            super(_Index, self).__init__(**kwargs)

        if hasvalue(ndim):
            self._ndim = ndim
        elif len(self) > 0:
            self._ndim = len(self.values()[0])
        else:
            raise ValueError('must provide index size or initial values')
        if checkany(self.values(), lambda x: len(x) != self._ndim): raise ValueError('index values size not match')

    # build-ins
    def __getitem__(self, item):
        if hashable(item) and self.has_key(item): return super(_Index, self).__getitem__(item)
        return _Index([(k,v[item]) for k,v in self.items()])

    def __setitem__(self, key, value):
        if isinstance(value, _Index):
            if checkany(self.keys(), lambda x: not value.has_key(x)): raise KeyError('index has different keys')
            for k in self.keys(): np.put(self[k], key, value[k])
        else:
            if len(value) != self._ndim: raise ValueError('index values size not match')
            super(_Index, self).__setitem__(key, value)

    def __add__(self, other):
        return self.insert(other)

    def __eq__(self, other):
        if len(self) != len(other) or set(self.keys()) != set(other.keys()) or \
           checkany(self.keys(), lambda x: np.any(self[x] != other[x])): return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    # properties
    @property
    def ndim(self):
        return self._ndim

    @property
    def shape(self):
        return len(self), self._ndim

    # publics
    @classmethod
    def stack(cls, idx1, idx2):
        if not isinstance(idx1, _Index) or not isinstance(idx2, _Index): raise TypeError('unknown index type(s)')
        return idx1.insert(idx2)

    def insert(self, other, ids = NA):
        if not isinstance(other, _Index): raise TypeError('insert object is not Index')
        if checkany(self.keys(), lambda x: not other.has_key(x)): raise KeyError('index has different keys')
        pos = optional(ids, self._ndim)
        return _Index([(k, np.insert(v, pos, other[k])) for k,v in self.items()])

    def drop(self, ids = NA):
        pos = optional(ids, self._ndim)
        return _Index([(k, np.delete(v, pos)) for k,v in self.items()])

    def copy(self):
        return _Index(self.items(), ndim = self.ndim)


# table class
class Table(object):
    def __init__(self, X, dtype = float, rownames = NA, colnames = NA, rowindex = NA, colindex = NA, metadata = NA):
        self._dmatx = np.array(X).astype(dtype)
        self._dtype = dtype
        self._metas = {} if isna(metadata) else dict(metadata)

        self._rndct = NA
        self.rownames = rownames
        self._cndct = NA
        self.colnames = colnames

        self._rindx = NA
        self.rowindex = rowindex
        self._cindx = NA
        self.colindex = colindex

    # privates
    def _parseIndices(self, idx):
        rids, cids = (idx, slice(None)) if not isinstance(idx, tuple) else \
                     (idx[0], slice(None)) if len(idx) == 1 else idx

        def _parse(ids, ndct):
            if not listable(ids): ids = [ids]
            ids = np.array(ids)

            if ids.shape[0] == 0: return []
            if ids.dtype.kind == 'i': return ids
            if ids.dtype.kind == 'b': return np.where(ids)[0]
            if hasvalue(ndct) and ids.dtype.kind in ('S', 'U'): return np.array([ndct[v] for v in ids])

            raise IndexError('unknown index type')

        rids = _parse(rids, self._rndct) if not isinstance(rids, slice) else np.arange(self.nrow)[rids]
        cids = _parse(cids, self._cndct) if not isinstance(cids, slice) else np.arange(self.ncol)[cids]
        return rids, cids

    # built-ins
    def __getitem__(self, item):
        rids, cids = self._parseIndices(item)
        return Table(self._dmatx[np.ix_(rids,cids)], dtype = self._dtype, metadata = self._metas,
                     rownames = self.rownames[rids], colnames = self.colnames[cids],
                     rowindex = self.rowindex[rids], colindex = self.colindex[cids])

    def __setitem__(self, key, value):
        rids, cids = self._parseIndices(key)
        if isinstance(value, Table):
            self._dmatx[np.ix_(rids,cids)] = value.values

            if hasvalue(self._rndct):
                if isna(value._rndct): raise KeyError('input table does not have row names')
                nams = self.rownames
                nams[rids] = value.rownames
                self.rownames = nams
            if hasvalue(self._cndct):
                if isna(value._cndct): raise KeyError('input table does not have column names')
                nams = self.colnames
                nams[cids] = value.colnames
                self.colnames = nams

            self.rowindex[rids] = value.rowindex
            self.colindex[cids] = value.colindex
        else:
            self._dmatx[np.ix_(rids,cids)] = value

    def __add__(self, other):
        return Table.vstack(self, other)

    def __len__(self):
        return self.nrow

    # def __str__(self):
    #     s = self.toStr(delimiter = '\t') + '\n' + \
    #         '[%s]: %d x %d' % (str(self._dtype), self.nrow, self.ncol)
    #     return s
    #
    # def __repr__(self):
    #     return str(self)

    def __array__(self):
        return self._dmatx # for np.array conversion

    # properties
    @property
    def values(self):
        return self._dmatx

    @values.setter
    def values(self, value):
        self._dmatx[:] = np.array(value, dtype = self._dtype)

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
        return np.array(self._rndct.keys()) if hasvalue(self._rndct) else NA

    @rownames.setter
    def rownames(self, value):
        if isna(value) or value is None:
            self._rndct = NA
        elif listable(value):
            if len(value) != self.nrow: raise KeyError('row names and data matrix size not match')
            if len(value) != len(set(value)): raise KeyError('row names have duplications')
            self._rndct = OrderedDict([(n,i) for i,n in enumerate(value)])
        else: raise TypeError('unknown names value type')

    @property
    def colnames(self):
        return np.array(self._cndct.keys()) if hasvalue(self._cndct) else NA

    @colnames.setter
    def colnames(self, value):
        if isna(value) or value is None:
            self._cndct = NA
        elif listable(value):
            if len(value) != self.ncol: raise KeyError('column names and data matrix size not match')
            if len(value) != len(set(value)): raise KeyError('column names have duplications')
            self._cndct = OrderedDict([(n,i) for i,n in enumerate(value)])
        else: raise TypeError('unknown names value type')

    @property
    def rowindex(self):
        return self._rindx

    @rowindex.setter
    def rowindex(self, value):
        if isinstance(value, _Index) and value.ndim == self.nrow:
            self._rindx = value.copy()
        else:
            self._rindx = _Index(value, ndim = self.nrow)

    @property
    def colindex(self):
        return self._cindx

    @colindex.setter
    def colindex(self, value):
        if isinstance(value, _Index) and value.ndim == self.ncol:
            self._cindx = value.copy()
        else:
            self._cindx = _Index(value, ndim = self.ncol)

    @property
    def metadata(self):
        return self._metas

    @property
    def T(self):
        tab = Table(self._dmatx.T, dtype = self._dtype, metadata = self._metas, rowindex = self.colindex, colindex = self.rowindex)
        tab._rndct, tab._cndct = self._cndct.copy(), self._rndct.copy()
        return tab

    # publics
    @classmethod
    def hstack(cls, tab1, tab2, force = False):
        if not isinstance(tab1, Table) or not isinstance(tab2, Table): raise TypeError('unknown table type(s)')

        if tab1.nrow != tab2.nrow: raise ValueError('input table has different number of rows')
        if not force and (np.any(tab1.rownames != tab2.rownames) or tab1.rowindex != tab2.rowindex):
           raise ValueError('input table has different row names / indices')

        tab = Table(np.hstack((tab1.values, tab2.values)), dtype = tab1._dtype,
                    rowindex = tab1.rowindex, colindex = tab1.colindex + tab2.colindex,
                    metadata = tab1._metas.items() + tab2._metas.items())
        tab._rndct = tab1._rndct.copy() if hasvalue(tab1._rndct) else NA

        if isna(tab1._cndct) and isna(tab2._cndct):
            tab._cndct = NA
        elif hasvalue(tab1._cndct) and hasvalue(tab2._cndct):
            tab._cndct = tab1._cndct.copy()
            for k,v in tab2._cndct.items(): tab._cndct[k] = v + tab1.ncol
            if len(tab._cndct) != len(tab1._cndct) + len(tab2._cndct): raise KeyError('input table has duplicate column names')
        else: raise KeyError('input table missing column names')

        return tab

    @classmethod
    def vstack(cls, tab1, tab2, force = False):
        if not isinstance(tab1, Table) or not isinstance(tab2, Table): raise TypeError('unknown table type(s)')

        if tab1.ncol != tab2.ncol: raise ValueError('input table has different number of columns')
        if not force and (np.any(tab1.colnames != tab2.colnames) or tab1.colindex != tab2.colindex):
           raise ValueError('input table has different column names / indices')

        tab = Table(np.vstack((tab1.values, tab2.values)), dtype = tab1._dtype,
                    rowindex = tab1.rowindex + tab2.rowindex, colindex = tab1.colindex,
                    metadata = tab1._metas.items() + tab2._metas.items())
        tab._cndct = tab1._cndct.copy() if hasvalue(tab1._cndct) else NA

        if isna(tab1._rndct) and isna(tab2._rndct):
            tab._rndct = NA
        elif hasvalue(tab1._rndct) and hasvalue(tab2._rndct):
            tab._rndct = tab1._rndct.copy()
            for k,v in tab2._rndct.items(): tab._rndct[k] = v + tab1.nrow
            if len(tab._rndct) != len(tab1._rndct) + len(tab2._rndct): raise KeyError('input table has duplicate row names')
        else: raise KeyError('input table missing row names')

        return tab

    # def insert(self, other, ids = NA, axis = 0):
    #     if not isinstance(other, tables):
    #
    #
    # def drop(self, ids, axis = 0):
    #     if axis == 0:
    #         return NamedArray(np.delete(self.values, ids, axis = 0), dtype = self.dtype, strfmt = self._sfmt,
    #                           rownames = np.delete(self.rownames, ids), colnames = self.colnames)
    #     elif axis == 1:
    #         return NamedArray(np.delete(self.values, ids, axis = 1), dtype = self.dtype, strfmt = self._sfmt,
    #                           rownames = self.rownames, colnames = np.delete(self.colnames, ids))
    #     else: raise IndexError('unsupported axis %d' % axis)
    #
    # def astype(self, dtype):
    #     ds = self.copy()
    #     ds.dtype = dtype
    #     return ds
    #
    # def copy(self):
    #     return Table(self._dmatx.copy(), self.)
    #
    #     return deepcopy(self)
    #
    # def toList(self, transpose = False):
    #     return list(map(list, (self.values.T if transpose else self.values)))
    #
    # def toStr(self, delimiter = ',', transpose = False):
    #     rn, cn = (self.rownames, self.colnames) if not transpose else (self.colnames, self.rownames)
    #     omtx = [[' '] + list(cn)] + \
    #            [[n] + list(l) for n,l in zip(rn, self.toList(transpose))]
    #     return join([join(map(str,ln), delimiter) for ln in omtx], '\n')
    #
    # def toFile(self, fname):
    #     checkOutputFile(fname)
    #     with open(fname, 'w') as f: cp.dump(self, f, protocol = cp.HIGHEST_PROTOCOL)
    #     return os.path.isfile(fname)
    #
    #
    #
    #
    #
    #
    #
# class _old():
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
#
#


