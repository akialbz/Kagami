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
from kagami.dtypes.factor import _Factor
from kagami.portals import textPortal, tablePortal


def _packArray(val):
    if isinstance(val, _Factor): return val
    if not isinstance(val, np.ndarray): val = np.array(val)
    if val.ndim == 0: val = val.reshape((1,))
    if val.dtype.kind == 'U': val = val.astype(str)
    return val


# table index class


# table class
class Table(object):
    def __init__(self, X, dtype = float, rownames = NA, colnames = NA, rowindex = NA, colindex = NA, metadata = NA):
        self._dmatx = np.array(X).astype(dtype)
        self._dtype = dtype # careful do not use _dmatx.dtype -> str converted to fix length S##
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
            if hasvalue(ndct) and ids.dtype.kind in ('S','U'): return np.array([ndct[str(v)] for v in ids])
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
                snams, vnams = self.rownames, value.rownames
                if snams.dtype.itemsize < vnams.dtype.itemsize: snams = snams.astype('S%d' % vnams.dtype.itemsize)
                snams[rids] = vnams
                self.rownames = snams
            if hasvalue(self._cndct):
                if isna(value._cndct): raise KeyError('input table does not have column names')
                snams, vnams = self.colnames, value.colnames
                if snams.dtype.itemsize < vnams.dtype.itemsize: snams = snams.astype('S%d' % vnams.dtype.itemsize)
                snams[cids] = vnams
                self.colnames = snams

            self.rowindex[rids] = value.rowindex
            self.colindex[cids] = value.colindex
        else:
            self._dmatx[np.ix_(rids,cids)] = value

    def __add__(self, other):
        return Table.vstack(self, other)

    def __eq__(self, other):
        if isinstance(other, Table):
            return self._dmatx == other.values
        elif isinstance(other, np.ndarray):
            return self._dmatx == other
        else: raise TypeError('comparison not supported')

    def __len__(self):
        return self.nrow

    def __str__(self):
        slns = self.toStr(delimiter = '\t', withIndex = True, asLines = True)
        if len(slns) > 20: slns = slns[:15] + ['', '...', ''] + slns[-2:]
        slns += ['Table([%s], shape = (%d x %d))' % (str(self._dtype), self.nrow, self.ncol)]
        return join(slns, '\n')

    def __repr__(self):
        return self.__str__()

    def __array__(self, dtype = None):
        dm = self._dmatx
        if dtype is not None: arr = dm.astype(dtype)
        return dm

    def __array_wrap__(self, arr):
        tab = self.copy()
        tab.values = arr
        return tab

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
    def shape(self):
        return self._dmatx.shape

    @property
    def ndim(self):
        return 2

    @property
    def rownames(self):
        return np.array(self._rndct.keys()) if hasvalue(self._rndct) else NA

    @rownames.setter
    def rownames(self, value):
        if isna(value) or value is None:
            self._rndct = NA
        elif listable(value):
            if len(value) != self.nrow: raise KeyError('row names and data matrix size not match')
            self._rndct = OrderedDict([(str(n),i) for i,n in enumerate(value)])
            if len(value) != len(self._rndct): raise KeyError('row names have duplications')
        else: raise TypeError('unknown row names data type')

    @property
    def colnames(self):
        return np.array(self._cndct.keys()) if hasvalue(self._cndct) else NA

    @colnames.setter
    def colnames(self, value):
        if isna(value) or value is None:
            self._cndct = NA
        elif listable(value):
            if len(value) != self.ncol: raise KeyError('column names and data matrix size not match')
            self._cndct = OrderedDict([(str(n),i) for i,n in enumerate(value)])
            if len(value) != len(self._cndct): raise KeyError('column names have duplications')
        else: raise TypeError('unknown column names data type')

    @property
    def rowindex(self):
        return self._rindx

    @rowindex.setter
    def rowindex(self, value):
        self._rindx = value.copy() if isinstance(value, _Index) and value.size == self.nrow else _Index(value, size = self.nrow)

    @property
    def colindex(self):
        return self._cindx

    @colindex.setter
    def colindex(self, value):
        self._cindx = value.copy() if isinstance(value, _Index) and value.size == self.ncol else _Index(value, size = self.ncol)

    @property
    def metadata(self):
        return self._metas

    @property
    def T(self):
        tab = Table(self._dmatx.T, dtype = self._dtype, metadata = self._metas, rowindex = self.colindex, colindex = self.rowindex)
        tab._rndct = self._rndct.copy() if hasvalue(self._rndct) else NA
        tab._cndct = self._cndct.copy() if hasvalue(self._cndct) else NA
        return tab

    # publics
    # class methods
    @classmethod
    def hstack(cls, tab1, tab2, ids = NA, force = False):
        return tab1.insert(tab2, ids = ids, axis = 1, force = force)

    @classmethod
    def vstack(cls, tab1, tab2, ids = NA, force = False):
        return tab1.insert(tab2, ids = ids, axis = 0, force = force)

    @classmethod
    def fromCSVFile(cls, fname):
        dm = tablePortal.load(fname, delimiter = ',')

    @classmethod
    def fromHDF5(cls, fname):
        pass

    # object methods
    def insert(self, other, ids = NA, axis = 0, force = False):
        if not isinstance(other, Table): raise TypeError('unknown table type')
        if axis not in (0, 1): raise IndexError('unsupport axis [%d]' % axis)

        pos = optional(ids, (self.nrow, self.ncol)[axis])
        ndm = np.insert(self.values, pos, other.values, axis = axis)

        if axis == 0:
            if not force and (np.any(self.colnames != other.colnames) or self.colindex != other.colindex):
               raise ValueError('input table has different column names / indices')

            tab = Table(ndm, dtype = self._dtype, metadata = self._metas.items() + other._metas.items(),
                        rowindex = self.rowindex.insert(other.rowindex, pos), colindex = self.colindex)

            tab._cndct = self._cndct.copy() if hasvalue(self._cndct) else NA

            if isna(self._rndct) and isna(other._rndct):
                tab._rndct = NA
            elif hasvalue(self._rndct) and hasvalue(other._rndct):
                tab._rndct = OrderedDict([(str(n),i) for i, n in enumerate(np.insert(self.rownames, pos, other.rownames))])
                if len(tab._rndct) != len(self._rndct) + len(other._rndct): raise KeyError('input table has duplicate row names')
            else: raise KeyError('input table missing row names')
        else:
            if not force and (np.any(self.rownames != other.rownames) or self.rowindex != other.rowindex):
               raise ValueError('input table has different row names / indices')

            tab = Table(ndm, dtype = self._dtype, metadata = self._metas.items() + other._metas.items(),
                        rowindex = self.rowindex, colindex = self.colindex.insert(other.colindex, pos))

            tab._rndct = self._rndct.copy() if hasvalue(self._rndct) else NA

            if isna(self._cndct) and isna(other._cndct):
                tab._cndct = NA
            elif hasvalue(self._cndct) and hasvalue(other._cndct):
                tab._cndct = OrderedDict([(str(n),i) for i, n in enumerate(np.insert(self.colnames, pos, other.colnames))])
                if len(tab._cndct) != len(self._cndct) + len(other._cndct): raise KeyError('input table has duplicate column names')
            else: raise KeyError('input table missing column names')

        return tab

    def drop(self, ids, axis = 0):
        if axis not in (0, 1): raise IndexError('unsupport axis [%d]' % axis)

        if axis == 0:
            tab = Table(np.delete(self.values, ids, axis = 0), dtype = self._dtype, metadata = self._metas,
                        rowindex = self.rowindex.drop(ids), colindex = self.colindex)
            tab._rndct = OrderedDict([(str(n),i) for i,n in enumerate(np.delete(self.rownames, ids))])
            tab._cndct = self._cndct.copy()
        else:
            tab = Table(np.delete(self.values, ids, axis = 1), dtype = self._dtype, metadata = self._metas,
                        rowindex = self.rowindex, colindex = self.colindex.drop(ids))
            tab._rndct = self._rndct.copy()
            tab._cndct = OrderedDict([(str(n),i) for i,n in enumerate(np.delete(self.colnames, ids))])

        return tab

    def astype(self, dtype):
        ds = self.copy()
        ds.dtype = dtype
        return ds

    def copy(self):
        tab = Table(self._dmatx.copy(), dtype = self._dtype, metadata = self._metas, rowindex = self.rowindex, colindex = self.colindex)
        tab._rndct, tab._cndct = self._rndct.copy(), self._cndct.copy()
        return tab

    def toList(self, transpose = False):
        olst = list(map(list,(self._dmatx.T if transpose else self._dmatx)))
        return olst if not transpose else list(map(list,zip(*olst)))

    def toStr(self, delimiter = ',', transpose = False, withIndex = False, asLines = False):
        smtx = [[''] + list(self.colnames)] + [[rn] + ln for rn, ln in zip(self.rownames, self.toList())]

        if withIndex:
            rindx = self.rowindex.toList(transpose = True)
            cindx = self.colindex.toList(transpose = False)
            if len(rindx) > 0: smtx = [ri + sl for ri,sl in zip(rindx, smtx)]
            if len(cindx) > 0: smtx = [[''] * len(self.rowindex) + ci for ci in cindx] + smtx

        if transpose: smtx = zip(*smtx)
        smtx = map(lambda x: join(map(str,x), delimiter), smtx)

        return smtx if asLines else join(smtx, '\n')

    def toCSVFile(self, fname, delimiter = ',', transpose = False, withIndex = False):
        checkOutputFile(fname)
        odm = self.toStr(delimiter = delimiter, transpose = transpose, withIndex = withIndex, asLines = True)
        textPortal.saveLines(fname, odm)
        return os.path.isfile(fname)

    def toHDF5(self, fname):
        checkOutputFile(fname)
        h5file = pytb.open_file(fname, mode = 'w')

        RowIndexTable = type('RowIndexTable', (pytb.IsDescription,), {k: pytb.Col.from_dtype(v.dtype) for k,v in self.rowindex.items()})
        ridtable = h5file.create_table('/', 'rowindex', RowIndexTable)
        ridlists = self.rowindex.toList(transpose = True)
        for ril in ridlists: ridtable.append(ril)

        ColIndexTable = type('ColIndexTable', (pytb.IsDescription,), {k: pytb.Col.from_dtype(v.dtype) for k,v in self.colindex.items()})
        cidtable = h5file.create_table('/', 'colindex', ColIndexTable)
        cidlists = self.colindex.toList(transpose = True)
        for cil in cidlists: cidtable.append(cil)

        values = h5file.create_array('/', 'values', self._dmatx)

        for k,v in self._metas.items(): setattr(values.attrs, k, v)

        h5file.close()
        return os.path.isfile(fname)

