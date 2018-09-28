#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
table

author(s): Albert (aki) Zhou
origin: 02-18-2017

"""


import os
import numpy as np
import tables as pytb
from collections import OrderedDict
from string import join
from kagami.core import NA, optional, isna, hasvalue, listable, hashable, checkany
from kagami.filesys import checkInputFile, checkOutputFile
from kagami.dtypes import CoreType, NamedIndex, StructuredArray
from kagami.portals import textPortal, tablePortal


# table class
class Table(CoreType):
    __slots__ = ('_dmatx', '_dtype', '_rnames', '_cnames', '_rindex', '_cindex', '_metas')

    def __init__(self, X, dtype = float, rownames = NA, colnames = NA, rowindex = NA, colindex = NA, metadata = NA):
        self._dmatx = np.array(X).astype(dtype)
        self._dtype = dtype # careful do not use _dmatx.dtype -> str converted to fix length S##
        self._metas = {} if isna(metadata) else dict(metadata)

        self._rnames = self._cnames = NA
        self.rownames = rownames
        self.colnames = colnames

        self._rindex = self._cindex = NA
        self.rowindex = rowindex
        self.colindex = colindex

    # privates
    def _parseIndices(self, idx):
        rids, cids = (idx, slice(None)) if not isinstance(idx, tuple) else \
                     (idx[0], slice(None)) if len(idx) == 1 else idx

        def _wrap(ids, nams):
            ids = np.array(ids)
            if ids.ndim != 1: ids = ids.reshape((1,))
            if ids.dtype.kind in ('i', 'u', 'b'): return ids
            if isna(nams): raise KeyError('input names not recongnised')
            return nams.idsof(ids)
        rids = np.arange(self.nrow)[rids] if isinstance(rids, slice) else _wrap(rids, self._rnames)
        cids = np.arange(self.ncol)[cids] if isinstance(cids, slice) else _wrap(cids, self._cnames)

        return rids, cids

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
        self._dmatx[np.ix_(rids, cids)] = np.array(value.values)
        if not isinstance(value, Table): return

        if hasvalue(self._rnames): self._rnames[rids] = value.rownames
        if hasvalue(self._cnames): self._cnames[cids] = value.colnames
        if hasvalue(self._rindex): self._rindex[:,rids] = value.rowindex
        if hasvalue(self._cindex): self._cindex[:,cids] = value.colindex

    def __delitem__(self, key):
        rids, cids = self._parseIndices(key)
        raxs = np.ones(self.nrow, dtype = bool)
        raxs[rids] = False
        caxs = np.ones(self.ncol, dtype = bool)
        caxs[cids] = False

        self._dmatx = self._dmatx[np.ix_(raxs, caxs)]
        if hasvalue(self._rnames): self._rnames = self._rnames[raxs]
        if hasvalue(self._cnames): self._cnames = self._cnames[caxs]
        if hasvalue(self._rindex): self._rindex = self._rindex[:,raxs]
        if hasvalue(self._cindex): self._cindex = self._cindex[:,caxs]

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
        if other.nrow != self.nrow: raise IndexError('input table has different number of rows')
        if hasvalue(other._rnames) and other._rnames != self._rnames: raise IndexError('input table has different row names')
        if hasvalue(other._rindex) and other._rindex != self._rindex: raise IndexError('input table has different row index')

        self._dmatx = np.c_[self._dmatx, other._dmatx]
        self._cnames += other._cnames
        self._cindex += other._cindex
        return self


    # TODO: continue from here

    def __str__(self):
        slns = self.toList(withIndex = True)
        if len(slns) > 15: slns = slns[:10] + ['...'] + slns[-2:]

        return join(map(lambda x: join(map(str,x), ', '), slns), '\n')

    def __repr__(self):
        slns = self.toList(withIndex = True)
        if len(slns) > 15: slns = slns[:10] + ['...'] + slns[-2:]

        rlns = ['Table(' + slns[0]] + \
               ['                ' + ln for ln in rlns[1:]]
        return join(rlns, '\n') + ', size = (%d, %d))' % (self.size, self.length)


        slns += ['Table([%s], shape = (%d x %d))' % (str(self._dtype), self.nrow, self.ncol)]

    # for numpy
    def __array__(self, dtype = None):
        raise NotImplementedError('method not implemented for Kagami CoreType')

    # for pickle
    def __getstate__(self):
        return {k: getattr(self, k) for k in self.__slots__}

    def __setstate__(self, dct):
        for k in filter(lambda x: x in self.__slots__, dct.keys()): setattr(self, k, dct[k])


    #
    # def __array__(self, dtype = None):
    #     dm = self._dmatx
    #     if dtype is not None: arr = dm.astype(dtype)
    #     return dm
    #
    # def __array_wrap__(self, arr):
    #     tab = self.copy()
    #     tab.values = arr
    #     return tab
    #

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
        self._rnames = NamedIndex(value) if hasvalue(value) else NA

    @property
    def colnames(self):
        return np.array(self._cnames)

    @colnames.setter
    def colnames(self, value):
        self._cnames = NamedIndex(value) if hasvalue(value) else NA

    @property
    def rowindex(self):
        return self._rindex

    @rowindex.setter
    def rowindex(self, value):
        self._rindex = StructuredArray(value) if hasvalue(value) else NA

    @property
    def colindex(self):
        return self._cindex

    @colindex.setter
    def colindex(self, value):
        self._cindex = StructuredArray(value) if hasvalue(value) else NA

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
    def toList(self, transpose = False, withIndex = False):
        smtx = [[''] + list(optional(self._cnames, np.arange(self.ncol)))] + \
               [[rn] + list(ln) for rn, ln in zip(optional(self._rnames, np.arange(self.nrow)), self._dmatx)]

        if withIndex:
            if hasvalue(self._rindex):
                ridx = map(list, zip(*[[n] + list(v) for n, v in zip(self._rindex.names, self._rindex.series)]))
                smtx = [ri + sl for ri, sl in zip(ridx, smtx)]
            if hasvalue(self._cindex):
                cidx = map(list, zip(*[[n] + list(v) for n, v in zip(self._cindex.names, self._cindex.series)])) if hasvalue(self._cindex) else NA
                smtx = [[''] * len(optional(self._rindex, [])) + ci for ci in cidx] + smtx

        if transpose: smtx = zip(*smtx)
        return smtx

    def toStr(self, delimiter = ',', transpose = False, withIndex = False):
        smtx = self.toList(transpose = transpose, withIndex = withIndex)
        return join(map(lambda x: join(map(str,x), delimiter), smtx), '\n')


    # # class methods
    # @classmethod
    # def hstack(cls, tab1, tab2, ids = NA, force = False):
    #     return tab1.insert(tab2, ids = ids, axis = 1, force = force)
    #
    # @classmethod
    # def vstack(cls, tab1, tab2, ids = NA, force = False):
    #     return tab1.insert(tab2, ids = ids, axis = 0, force = force)
    #
    # @classmethod
    # def fromCSVFile(cls, fname):
    #     dm = tablePortal.load(fname, delimiter = ',')
    #
    # @classmethod
    # def fromHDF5(cls, fname):
    #     pass
    #
    # # object methods
    # def insert(self, other, ids = NA, axis = 0, force = False):
    #     if not isinstance(other, Table): raise TypeError('unknown table type')
    #     if axis not in (0, 1): raise IndexError('unsupport axis [%d]' % axis)
    #
    #     pos = optional(ids, (self.nrow, self.ncol)[axis])
    #     ndm = np.insert(self.values, pos, other.values, axis = axis)
    #
    #     if axis == 0:
    #         if not force and (np.any(self.colnames != other.colnames) or self.colindex != other.colindex):
    #            raise ValueError('input table has different column names / indices')
    #
    #         tab = Table(ndm, dtype = self._dtype, metadata = self._metas.items() + other._metas.items(),
    #                     rowindex = self.rowindex.insert(other.rowindex, pos), colindex = self.colindex)
    #
    #         tab._cndct = self._cndct.copy() if hasvalue(self._cndct) else NA
    #
    #         if isna(self._rndct) and isna(other._rndct):
    #             tab._rndct = NA
    #         elif hasvalue(self._rndct) and hasvalue(other._rndct):
    #             tab._rndct = OrderedDict([(str(n),i) for i, n in enumerate(np.insert(self.rownames, pos, other.rownames))])
    #             if len(tab._rndct) != len(self._rndct) + len(other._rndct): raise KeyError('input table has duplicate row names')
    #         else: raise KeyError('input table missing row names')
    #     else:
    #         if not force and (np.any(self.rownames != other.rownames) or self.rowindex != other.rowindex):
    #            raise ValueError('input table has different row names / indices')
    #
    #         tab = Table(ndm, dtype = self._dtype, metadata = self._metas.items() + other._metas.items(),
    #                     rowindex = self.rowindex, colindex = self.colindex.insert(other.colindex, pos))
    #
    #         tab._rndct = self._rndct.copy() if hasvalue(self._rndct) else NA
    #
    #         if isna(self._cndct) and isna(other._cndct):
    #             tab._cndct = NA
    #         elif hasvalue(self._cndct) and hasvalue(other._cndct):
    #             tab._cndct = OrderedDict([(str(n),i) for i, n in enumerate(np.insert(self.colnames, pos, other.colnames))])
    #             if len(tab._cndct) != len(self._cndct) + len(other._cndct): raise KeyError('input table has duplicate column names')
    #         else: raise KeyError('input table missing column names')
    #
    #     return tab
    #
    # def drop(self, ids, axis = 0):
    #     if axis not in (0, 1): raise IndexError('unsupport axis [%d]' % axis)
    #
    #     if axis == 0:
    #         tab = Table(np.delete(self.values, ids, axis = 0), dtype = self._dtype, metadata = self._metas,
    #                     rowindex = self.rowindex.drop(ids), colindex = self.colindex)
    #         tab._rndct = OrderedDict([(str(n),i) for i,n in enumerate(np.delete(self.rownames, ids))])
    #         tab._cndct = self._cndct.copy()
    #     else:
    #         tab = Table(np.delete(self.values, ids, axis = 1), dtype = self._dtype, metadata = self._metas,
    #                     rowindex = self.rowindex, colindex = self.colindex.drop(ids))
    #         tab._rndct = self._rndct.copy()
    #         tab._cndct = OrderedDict([(str(n),i) for i,n in enumerate(np.delete(self.colnames, ids))])
    #
    #     return tab
    #
    # def astype(self, dtype):
    #     ds = self.copy()
    #     ds.dtype = dtype
    #     return ds
    #
    # def copy(self):
    #     tab = Table(self._dmatx.copy(), dtype = self._dtype, metadata = self._metas, rowindex = self.rowindex, colindex = self.colindex)
    #     tab._rndct, tab._cndct = self._rndct.copy(), self._cndct.copy()
    #     return tab
    #
    #
    # def toCSVFile(self, fname, delimiter = ',', transpose = False, withIndex = False):
    #     checkOutputFile(fname)
    #     odm = self.toStr(delimiter = delimiter, transpose = transpose, withIndex = withIndex, asLines = True)
    #     textPortal.saveLines(fname, odm)
    #     return os.path.isfile(fname)
    #
    # def toHDF5(self, fname):
    #     checkOutputFile(fname)
    #     h5file = pytb.open_file(fname, mode = 'w')
    #
    #     RowIndexTable = type('RowIndexTable', (pytb.IsDescription,), {k: pytb.Col.from_dtype(v.dtype) for k,v in self.rowindex.items()})
    #     ridtable = h5file.create_table('/', 'rowindex', RowIndexTable)
    #     ridlists = self.rowindex.toList(transpose = True)
    #     for ril in ridlists: ridtable.append(ril)
    #
    #     ColIndexTable = type('ColIndexTable', (pytb.IsDescription,), {k: pytb.Col.from_dtype(v.dtype) for k,v in self.colindex.items()})
    #     cidtable = h5file.create_table('/', 'colindex', ColIndexTable)
    #     cidlists = self.colindex.toList(transpose = True)
    #     for cil in cidlists: cidtable.append(cil)
    #
    #     values = h5file.create_array('/', 'values', self._dmatx)
    #
    #     for k,v in self._metas.items(): setattr(values.attrs, k, v)
    #
    #     h5file.close()
    #     return os.path.isfile(fname)
    #
