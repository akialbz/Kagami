#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
table

author(s): Albert (aki) Zhou
origin: 02-18-2017

"""


import logging, os
import numpy as np
import tables as ptb
from string import join
from types import NoneType
from kagami.core import NA, NAType, optional, isna, hasvalue, autoeval
from kagami.filesys import checkInputFile, checkOutputFile
from kagami.dtypes import CoreType, NamedIndex, StructuredArray
from kagami.portals import tablePortal


# table class
class Table(CoreType):
    __slots__ = ('_dmatx', '_dtype', '_rnames', '_cnames', '_rindex', '_cindex', '_metas')

    def __init__(self, X, dtype = float, rownames = NA, colnames = NA, rowindex = NA, colindex = NA, metadata = NA):
        self._dmatx = np.array(X).astype(dtype)
        if self._dmatx.ndim != 2: raise ValueError('input data is not a 2-dimensional matrix')

        self._dtype = dtype # careful do not use _dmatx.dtype -> str converted to fix length S##
        self._metas = {} if isna(metadata) else dict(metadata)

        self._rnames = self._cnames = NA
        self.rownames = rownames
        self.colnames = colnames

        self._rindex = self._cindex = NA
        self.rowindex = rowindex
        self.colindex = colindex

    # privates
    def _parseIndices(self, idx, mapSlice = True):
        rids, cids = (idx, slice(None)) if not isinstance(idx, tuple) else \
                     (idx[0], slice(None)) if len(idx) == 1 else idx

        def _wrap(ids, nams):
            ids = np.array(ids)
            if ids.ndim != 1: ids = ids.reshape((1,))
            if ids.dtype.kind in ('i', 'u', 'b'): return ids
            if isna(nams): raise KeyError('input names not recongnised')
            return nams.idsof(ids)

        rids = _wrap(rids, self._rnames) if not isinstance(rids, slice) else \
               np.arange(self.nrow)[rids] if mapSlice else rids
        cids = _wrap(cids, self._cnames) if not isinstance(cids, slice) else \
               np.arange(self.ncol)[cids] if mapSlice else cids

        return rids, cids

    def _toStrList(self, delimiter, transpose = False, withIndex = True):
        slns = map(lambda x: map(str,x), self.tolist(transpose = transpose, withindex = withIndex))

        vfmt = '%%%ds' % (np.max(map(lambda x: map(len,x), slns)) + 1)
        _fmtlns = lambda lns: list(map(lambda x: '[' + join(map(lambda v: vfmt % v, x), delimiter) + ']', lns))

        slns = _fmtlns(slns) if len(slns) <= 15 else \
               _fmtlns(slns[:10]) + [' ... '] + _fmtlns(slns[-2:])
        return slns

    # built-ins
    def __getitem__(self, item):
        rids, cids = self._parseIndices(item)
        ntab = Table(self._dmatx[np.ix_(rids, cids)], dtype = self._dtype, metadata = self._metas)

        if hasvalue(self._rnames): ntab.rownames = self._rnames[rids]
        if hasvalue(self._cnames): ntab.colnames = self._cnames[cids]
        if hasvalue(self._rindex): ntab.rowindex = self._rindex[:,rids]
        if hasvalue(self._cindex): ntab.colindex = self._cindex[:,cids]
        return ntab

    def __setitem__(self, key, value):
        rids, cids = self._parseIndices(key)
        if not isinstance(value, Table):
            self._dmatx[np.ix_(rids, cids)] = np.array(value)
        else:
            self._dmatx[np.ix_(rids, cids)] = np.array(value.values)
            if hasvalue(self._rnames): self._rnames[rids] = value.rownames
            if hasvalue(self._cnames): self._cnames[cids] = value.colnames
            if hasvalue(self._rindex): self._rindex[:,rids] = value.rowindex
            if hasvalue(self._cindex): self._cindex[:,cids] = value.colindex

    def __delitem__(self, key):
        rids, cids = self._parseIndices(key, mapSlice = False)
        rlic = isinstance(rids, slice) and rids == slice(None)
        clic = isinstance(cids, slice) and cids == slice(None)

        if rlic and clic:
            self._dmatx = np.array([], dtype = self._dtype).reshape((0,0))
            if hasvalue(self._rnames): del self._rnames[:]
            if hasvalue(self._cnames): del self._cnames[:]
            if hasvalue(self._rindex): del self._rindex[:,np.arange(self.nrow)]
            if hasvalue(self._cindex): del self._cindex[:,np.arange(self.ncol)]
            return

        if not rlic:
            self._dmatx = np.delete(self._dmatx, rids, axis = 0)
            if hasvalue(self._rnames): del self._rnames[rids]
            if hasvalue(self._rindex): del self._rindex[:,rids]
        if not clic:
            self._dmatx = np.delete(self._dmatx, cids, axis = 1)
            if hasvalue(self._cnames): del self._cnames[cids]
            if hasvalue(self._cindex): del self._cindex[:,cids]

    def __iter__(self):
        return iter(self._dmatx)

    def __contains__(self, item):
        return np.any(self._dmatx == item)

    def __len__(self):
        return self.shape[0]

    def __eq__(self, other):
        if not isinstance(other, Table): return self._dmatx == other
        return self.shape == other.shape and np.all(self._dmatx == other._dmatx) and \
               np.all(self._rnames == other._rnames) and np.all(self._cnames == other._cnames) and \
               self._rindex == other._rindex and self._cindex == other._cindex

    def __iadd__(self, other):
        if not isinstance(other, Table): raise TypeError('unknown input data type')
        if other.ncol != self.ncol: raise IndexError('input table has different number of columns')
        if hasvalue(other._cnames) and other._cnames != self._cnames: raise IndexError('input table has different column names')
        if hasvalue(other._cindex) and other._cindex != self._cindex: raise IndexError('input table has different column index')

        self._dmatx = np.r_[self._dmatx, other._dmatx]
        if hasvalue(self._rnames): self._rnames += other._rnames
        if hasvalue(self._rindex): self._rindex += other._rindex
        return self

    def __str__(self):
        return self.tostr(delimiter = ',', transpose = False, withindex = True)

    def __repr__(self):
        rlns = self._toStrList(delimiter = ',')
        rlns = ['Table([' + rlns[0]] + \
               ['       ' + ln for ln in rlns[1:]]
        return join(rlns, '\n') + '], size = (%d, %d))' % (self.nrow, self.ncol)

    # for numpy
    def __array__(self, dtype = None):
        return self._dmatx.copy() if dtype is None else self._dmatx.astype(dtype)

    # for pickle
    def __getstate__(self):
        return {k: getattr(self, k) for k in self.__slots__}

    def __setstate__(self, dct):
        for k in filter(lambda x: x in self.__slots__, dct.keys()): setattr(self, k, dct[k])

    # properties
    @property
    def values(self):
        return self._dmatx

    @values.setter
    def values(self, value):
        self._dmatx[:] = value

    @property
    def dtype(self):
        return self._dtype

    @dtype.setter
    def dtype(self, value):
        self._dmatx = self._dmatx.astype(value)
        self._dtype = value

    @property
    def nrow(self):
        return self.shape[0]

    @property
    def ncol(self):
        return self.shape[1]

    @property
    def size(self):
        return self.shape[0]

    @property
    def shape(self):
        return self._dmatx.shape

    @property
    def ndim(self):
        return 2

    @property
    def rownames(self):
        return np.array(self._rnames)

    @rownames.setter
    def rownames(self, value):
        if isna(value): self._rnames = NA; return
        self._rnames = NamedIndex(value)
        if self._rnames.size != self.nrow: raise ValueError('input row names size not match')

    @property
    def colnames(self):
        return np.array(self._cnames)

    @colnames.setter
    def colnames(self, value):
        if isna(value): self._cnames = NA; return
        self._cnames = NamedIndex(value)
        if self._cnames.size != self.ncol: raise ValueError('input column names size not match')

    @property
    def rowindex(self):
        return self._rindex

    @rowindex.setter
    def rowindex(self, value):
        if isna(value): self._rindex = NA; return
        self._rindex = StructuredArray(value)
        if self._rindex.length != self.nrow: raise ValueError('input row index size not match')

    @property
    def colindex(self):
        return self._cindex

    @colindex.setter
    def colindex(self, value):
        if isna(value): self._cindex = NA; return
        self._cindex = StructuredArray(value)
        if self._cindex.length != self.ncol: raise ValueError('input column index size not match')

    @property
    def metadata(self):
        return self._metas

    @property
    def T(self):
        tab = Table(self._dmatx.T, dtype = self._dtype, metadata = self._metas)
        tab._rnames, tab._cnames = self._cnames.copy(), self._rnames.copy()
        tab._rindex, tab._cindex = self._cindex.copy(), self._rindex.copy()
        return tab

    # publics
    def append(self, other, axis = 0):
        if not isinstance(other, Table): raise TypeError('unknown input data type')
        if axis == 0:
            if other.ncol != self.ncol: raise IndexError('input table has different number of columns')
            if hasvalue(other._cnames) and other._cnames != self._cnames: raise IndexError('input table has different column names')
            if hasvalue(other._cindex) and other._cindex != self._cindex: raise IndexError('input table has different column index')

            tab = Table(np.r_[self._dmatx, other._dmatx], dtype = self._dtype, metadata = self._metas)
            if hasvalue(self._rnames): tab.rownames = self._rnames + other._rnames
            if hasvalue(self._cnames): tab.colnames = self._cnames.copy()
            if hasvalue(self._rindex): tab.rowindex = self._rindex + other._rindex
            if hasvalue(self._cindex): tab.colindex = self._cindex.copy()
            return tab
        elif axis == 1:
            if other.nrow != self.nrow: raise IndexError('input table has different number of rows')
            if hasvalue(other._rnames) and other._rnames != self._rnames: raise IndexError('input table has different row names')
            if hasvalue(other._rindex) and other._rindex != self._rindex: raise IndexError('input table has different row index')

            tab = Table(np.c_[self._dmatx, other._dmatx], dtype = self._dtype, metadata = self._metas)
            if hasvalue(self._rnames): tab.rownames = self._rnames.copy()
            if hasvalue(self._cnames): tab.colnames = self._cnames + other._cnames
            if hasvalue(self._rindex): tab.rowindex = self._rindex.copy()
            if hasvalue(self._cindex): tab.colindex = self._cindex + other._cindex
            return tab
        else: raise IndexError('unsupported axis [%d]' % axis)

    def insert(self, other, pos = NA, axis = 0):
        if not isinstance(other, Table): raise TypeError('unknown input data type')
        if axis == 0:
            if other.ncol != self.ncol: raise IndexError('input table has different number of columns')
            if hasvalue(other._cnames) and other._cnames != self._cnames: raise IndexError('input table has different column names')
            if hasvalue(other._cindex) and other._cindex != self._cindex: raise IndexError('input table has different column index')

            if isna(pos): pos = self.nrow
            tab = Table(np.insert(self._dmatx, pos, other._dmatx, axis = 0), dtype = self._dtype, metadata = self._metas)
            if hasvalue(self._rnames): tab.rownames = self._rnames.insert(other._rnames, pos) # in case np.inert etc will change array shape
            if hasvalue(self._cnames): tab.colnames = self._cnames.copy()
            if hasvalue(self._rindex): tab.rowindex = self._rindex.insert(other._rindex, pos)
            if hasvalue(self._cindex): tab.colindex = self._cindex.copy()
            return tab
        elif axis == 1:
            if other.nrow != self.nrow: raise IndexError('input table has different number of rows')
            if hasvalue(other._rnames) and other._rnames != self._rnames: raise IndexError('input table has different row names')
            if hasvalue(other._rindex) and other._rindex != self._rindex: raise IndexError('input table has different row index')

            if isna(pos): pos = self.ncol
            tab = Table(np.insert(self._dmatx, pos, other._dmatx, axis = 1), dtype = self._dtype, metadata = self._metas)
            if hasvalue(self._rnames): tab.rownames = self._rnames.copy()
            if hasvalue(self._cnames): tab.colnames = self._cnames.insert(other._cnames, pos)
            if hasvalue(self._rindex): tab.rowindex = self._rindex.copy()
            if hasvalue(self._cindex): tab.colindex = self._cindex.insert(other._cindex, pos)
            return tab
        else: raise IndexError('unsupported axis [%d]' % axis)

    def drop(self, pos, axis = 0):
        if axis == 0:
            if isna(pos): pos = self.nrow
            tab = Table(np.delete(self._dmatx, pos, axis = 0), dtype = self._dtype, metadata = self._metas)
            if hasvalue(self._rnames): tab.rownames = self._rnames.drop(pos)
            if hasvalue(self._cnames): tab.colnames = self._cnames.copy()
            if hasvalue(self._rindex): tab.rowindex = self._rindex.drop(pos)
            if hasvalue(self._cindex): tab.colindex = self._cindex.copy()
            return tab
        elif axis == 1:
            if isna(pos): pos = self.ncol
            tab = Table(np.delete(self._dmatx, pos, axis = 1), dtype = self._dtype, metadata = self._metas)
            if hasvalue(self._rnames): tab.rownames = self._rnames.copy()
            if hasvalue(self._cnames): tab.colnames = self._cnames.drop(pos)
            if hasvalue(self._rindex): tab.rowindex = self._rindex.copy()
            if hasvalue(self._cindex): tab.colindex = self._cindex.drop(pos)
            return tab
        else: raise IndexError('unsupported axis [%d]' % axis)

    def copy(self):
        tab = Table(self._dmatx, dtype = self._dtype, metadata = self._metas)
        tab._rnames, tab._cnames = self._rnames.copy(), self._cnames.copy()
        tab._rindex, tab._cindex = self._rindex.copy(), self._cindex.copy()
        return tab

    def astype(self, dtype):
        ds = self.copy()
        ds.dtype = dtype
        return ds

    def tolist(self, transpose = False, withindex = False):
        smtx = [['#'] + list(optional(self._cnames, np.arange(self.ncol)))] + \
               [[rn]  + list(ln) for rn, ln in zip(optional(self._rnames, np.arange(self.nrow)), self._dmatx)]

        if withindex:
            if hasvalue(self._rindex):
                ridx = map(list, zip(*[['<%s>' % n] + list(v) for n, v in zip(self._rindex.names, self._rindex.series)]))
                smtx = [ri + sl for ri, sl in zip(ridx, smtx)]
            if hasvalue(self._cindex):
                cidx = map(list, [['<%s>' % n] + list(v) for n, v in zip(self._cindex.names, self._cindex.series)])
                smtx = [[''] * len(optional(self._rindex, [])) + ci for ci in cidx] + smtx

        if transpose: smtx = zip(*smtx)
        return smtx

    def tostr(self, delimiter = ',', transpose = False, withindex = False):
        rlns = self._toStrList(delimiter = delimiter, transpose = transpose, withIndex = withindex)
        rlns = ['[' + rlns[0]] + \
               [' ' + ln for ln in rlns[1:]]
        return join(rlns, '\n') + ']'

    # portals
    @classmethod
    def fromsarray(cls, array, rowindex = NA, colindex = NA):
        if isna(rowindex) or isna(colindex): rowindex, colindex = np.where(array == '#')
        ridx = StructuredArray.fromsarray(array[colindex:,:rowindex].T) if rowindex > 0 else NA
        cidx = StructuredArray.fromsarray(array[:colindex,rowindex:])   if colindex > 0 else NA
        array = array[colindex:,rowindex:]

        rnam = array[0,1:]
        if np.all(rnam == np.arange(rnam.shape[0]).astype(str)): rnam = NA
        cnam = array[1:,0]
        if np.all(cnam == np.arange(cnam.shape[0]).astype(str)): cnam = NA
        array = array[1:,1:]

        dtype = type(autoeval(array[0,0]))
        if dtype in (NAType, NoneType): logging.warning('invalid data type detected')

        return Table(array, dtype = dtype, rownames = rnam, colnames = cnam, rowindex = ridx, colindex = cidx)

    def tosarray(self, withindex = True):
        return np.array(self.tolist(transpose = False, withindex = withindex), dtype = str)

    @classmethod
    def loadcsv(cls, fname, delimiter = ',', transposed = False, rowindex = 0, colindex = 0):
        idm = np.array(tablePortal.load(fname, delimiter = delimiter))
        if transposed: idm = idm.T
        return cls.fromsarray(idm, rowindex = rowindex, colindex = colindex)

    def savecsv(self, fname, delimiter = ',', transpose = False, withindex = True):
        odm = self.tosarray(withindex)
        if transpose: odm = odm.T
        tablePortal.save(odm, fname, delimiter = delimiter)
        return os.path.isfile(fname)

    @classmethod
    def loadhdf(cls, fname):
        checkInputFile(fname)
        hdf = ptb.open_file(fname, mode = 'r')

        darr = hdf.root.DataMatx.read()
        meta = [(n, getattr(hdf.root.DataMatx.attrs, n)) for n in hdf.root.DataMatx.attrs._f_list('user')]

        rnam = hdf.root.RowNames.read() if hasattr(hdf.root, 'RowNames') else NA
        cnam = hdf.root.ColNames.read() if hasattr(hdf.root, 'ColNames') else NA
        ridx = StructuredArray.fromhtable(hdf.root.RowIndex) if hasattr(hdf.root, 'RowIndex') else NA
        cidx = StructuredArray.fromhtable(hdf.root.ColIndex) if hasattr(hdf.root, 'ColIndex') else NA

        hdf.close()
        return Table(darr, metadata = meta, rownames = rnam, colnames = cnam, rowindex = ridx, colindex = cidx)

    def savehdf(self, fname, compression = 0):
        checkOutputFile(fname)
        hdf = ptb.open_file(fname, mode = 'w')

        darr = hdf.create_array(hdf.root, 'DataMatx', self._dmatx)
        for k,v in self._metas.items(): setattr(darr.attrs, k, v)

        if hasvalue(self._rnames): hdf.create_array(hdf.root, 'RowNames', self._rnames)
        if hasvalue(self._cnames): hdf.create_array(hdf.root, 'ColNames', self._cnames)
        if hasvalue(self._rindex): self._rindex.tohtable(hdf.root, 'RowIndex', compression)
        if hasvalue(self._cindex): self._cindex.tohtable(hdf.root, 'ColIndex', compression)

        hdf.close()
        return os.path.isfile(fname)
