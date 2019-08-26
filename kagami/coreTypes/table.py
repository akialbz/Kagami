#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
table

author(s): Albert (aki) Zhou
origin: 02-18-2017

"""


from __future__ import annotations

import logging, os
import numpy as np
import tables as ptb
from typing import Iterable, Mapping, Union, Optional
from pathlib import Path
from operator import itemgetter
from kagami.common import l, ll, optional, missing, available, isstring, listable, checkany, paste, smap, collapse, partial, checkInputFile, checkOutputFile, Metadata
from kagami.portals import tablePortal
from .coreType import CoreType, Indices2D
from .namedIndex import NamedIndex
from .structArray import StructuredArray


__all__ = ['Table']


# table class
class Table(CoreType):
    __slots__ = ('_dmatx', '_rnames', '_cnames', '_rindex', '_cindex', '_metas', '_memmap')

    def __init__(self, X: Iterable[Iterable], dtype: Optional[Union[str, type, np.ndarray.dtype]] = None,
                 rownames: Optional[Union[Iterable[str], NamedIndex]] = None, colnames: Optional[Union[Iterable[str], NamedIndex]] = None,
                 rowindex: Optional[StructuredArray] = None, colindex: Optional[StructuredArray] = None,
                 metas: Optional[Mapping] = None, memmap: Optional[Union[str, Path]] = None):
        if not isinstance(X, np.ndarray): X = smap(X, ll)
        self._dmatx = np.asarray(X, dtype = dtype)
        if self._dmatx.ndim != 2: raise ValueError('input data is not a 2-dimensional matrix')

        self._memmap = None
        if available(memmap): self.offload(Path(memmap))

        self._rnames = self._cnames = None
        self.rownames = rownames
        self.colnames = colnames

        self._rindex = self._cindex = None
        self.rowindex = rowindex
        self.colindex = colindex

        self._metas = Metadata(optional(metas, ()))

    # privates
    def _parseids(self, idx, mapslice = True):
        rids, cids = (idx, slice(None)) if not isinstance(idx, tuple) else \
                     (idx[0], slice(None)) if len(idx) == 1 else idx

        def _wrap(ids, num, names):
            if isinstance(ids, slice): return ids if not mapslice else np.arange(num)[ids]
            if not listable(ids): ids = [ids]
            if not checkany(ids, isstring): return ids
            if missing(names): raise KeyError('table names not set')
            return names.idsof(ids, safe = False)

        rids = _wrap(rids, self.nrow, self._rnames)
        cids = _wrap(cids, self.ncol, self._cnames)
        return rids, cids

    def _tostrlns(self, delimiter, transpose = False, withindex = True, strinkrows = 15, strinkcols = 10):
        def _fmt(mtx, rnam, cnam, ridx, cidx):
            nr, nc = mtx.shape

            if missing(rnam): rnam = smap(range(nr), lambda x: f'#{x}')
            if missing(cnam): cnam = smap(range(nc), lambda x: f'#{x}')

            _sln = lambda x,sr,hd,tl,rp: (smap(x[:hd],str) + [rp] + smap(x[tl:],str)) if sr else smap(x, str)
            _scol = lambda x: _sln(x, nc > strinkcols, 3, -1, ' ... ')
            _srow = lambda x: _sln(x, nr > strinkrows, 5, -3, '')

            slns = [_scol(cnam)] + \
                 (([_scol(ln) for ln in mtx[:5]] + [_scol([' ... ... '] + [''] * (nc-1))] + [_scol(ln) for ln in mtx[-3:]]) if nr > 15 else \
                   [_scol(ln) for ln in mtx])
            slns = [['#'] + slns[0]] + [[n] + ln for n,ln in zip(_srow(rnam), slns[1:])]

            nri = ridx.size if available(ridx) else 0
            nci = cidx.size if available(cidx) else 0

            if nci > 0: slns = [[f'<{k}>'] + _scol(cidx[k]) for k in cidx.names] + slns
            if nri > 0:
                sidx = [['' * nci] + [f'<{k}>'] + _srow(ridx[k]) for k in ridx.names]
                slns = [list(ix) + ln for ix,ln in zip(zip(*sidx), slns)]

            def _sfmt(lns, pos):
                size = max(collapse(smap(lns, lambda x: smap(x[pos], lambda v: len(v) if v not in (' ... ', ' ... ... ') else 0)))) + 1
                for ln in lns: ln[pos] = smap(ln[pos], lambda x: '{0:>{1}s}'.format(x, size) if x != ' ... ' else x)
                return lns

            if nri > 0: slns = _sfmt(slns, slice(None,nri))
            slns = _sfmt(slns, slice(nri,nri+1))
            slns = _sfmt(slns, slice(nri+1,None))

            return smap(slns, lambda ln: paste(*ln, delimiter))

        sdm = _fmt(self._dmatx, self._rnames, self._cnames, self._rindex if withindex else None, self._cindex if withindex  else None) if not transpose else \
              _fmt(self._dmatx.T, self._cnames, self._rnames, self._cindex if withindex else None, self._rindex if withindex else None)
        return sdm

    # portals
    def onload(self, removefile: bool = True) -> Table:
        if not isinstance(self._dmatx, np.memmap): logging.warning('Table not offloaded, skip'); return self
        checkInputFile(self._memmap.file)

        mdmatx = np.memmap(self._memmap.file, dtype = self._memmap.dtype, mode = 'r', shape = self._memmap.shape)
        self._dmatx = np.array(mdmatx)
        del mdmatx

        if removefile: self._memmap.file.unlink()
        self._memmap = None
        return self

    def offload(self, fname: Union[str, Path]) -> Table:
        if isinstance(self._dmatx, np.memmap): logging.warning('Table already offloaded, skip'); return self
        checkOutputFile(fname)

        self._memmap = Metadata(file = fname, dtype = self._dmatx.dtype, shape = self._dmatx.shape)
        mdmatx = np.memmap(self._memmap.file, dtype = self._memmap.dtype, mode = 'w+', shape = self._memmap.shape)
        mdmatx[:] = self._dmatx[:]

        del self._dmatx
        self._dmatx = mdmatx
        return self





    # built-ins
    def __getitem__(self, item):
        rids, cids = self._parseIndices(item)
        ntab = Table(self._dmatx[np.ix_(rids, cids)], dtype = self.dtype, metadata = self._metas, fixRepeat = self._fixrep)

        if available(self._rnames): ntab.rownames = self._rnames[rids]
        if available(self._cnames): ntab.colnames = self._cnames[cids]
        if available(self._rindex): ntab.rowindex = self._rindex[:,rids]
        if available(self._cindex): ntab.colindex = self._cindex[:,cids]
        return ntab

    def __setitem__(self, key, value):
        if isinstance(key, np.ndarray) and key.shape == self.shape and key.dtype.kind == 'b' and \
           isinstance(value, (int, float, basestring, bool)): self._dmatx[key] = value; return # just for convenience

        rids, cids = self._parseIndices(key)
        if not isinstance(value, Table):
            self._dmatx[np.ix_(rids, cids)] = np.array(value)
        else:
            self._dmatx[np.ix_(rids, cids)] = np.array(value.X_)
            if available(self._rnames): self._rnames[rids] = value.rownames
            if available(self._cnames): self._cnames[cids] = value.colnames
            if available(self._rindex): self._rindex[:,rids] = value.rowindex
            if available(self._cindex): self._cindex[:,cids] = value.colindex

    def __delitem__(self, key):
        rids, cids = self._parseIndices(key, mapSlice = False)
        rlic = isinstance(rids, slice) and rids == slice(None)
        clic = isinstance(cids, slice) and cids == slice(None)

        if rlic and clic:
            self._dmatx = np.array([], dtype = self.dtype).reshape((0,0))
            if available(self._rnames): del self._rnames[:]
            if available(self._cnames): del self._cnames[:]
            if available(self._rindex): del self._rindex[:,np.arange(self.nrow)]
            if available(self._cindex): del self._cindex[:,np.arange(self.ncol)]
            return

        if not rlic:
            self._dmatx = np.delete(self._dmatx, rids, axis = 0)
            if available(self._rnames): del self._rnames[rids]
            if available(self._rindex): del self._rindex[:,rids]
        if not clic:
            self._dmatx = np.delete(self._dmatx, cids, axis = 1)
            if available(self._cnames): del self._cnames[cids]
            if available(self._cindex): del self._cindex[:,cids]

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

    def __lt__(self, other):
        return self._dmatx < other

    def __gt__(self, other):
        return self._dmatx > other

    def __le__(self, other):
        return self._dmatx <= other

    def __ge__(self, other):
        return self._dmatx >= other

    def __iadd__(self, other):
        if not isinstance(other, Table): raise TypeError('unknown input data type')
        if other.ncol != self.ncol: raise IndexError('input table has different number of columns')
        if available(self._cnames) and available(other._cnames) and np.any(other._cnames != self._cnames): raise IndexError('input table has different column names')
        if available(self._cindex) and available(other._cindex) and other._cindex != self._cindex: raise IndexError('input table has different column index')

        self._dmatx = np.r_[self._dmatx, other._dmatx]
        if available(self._rnames): self._rnames += other._rnames
        if available(self._rindex): self._rindex += other._rindex
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

    # properties
    @property
    def values(self):
        return self._dmatx.copy()

    @property
    def X_(self):
        return self._dmatx

    @X_.setter
    def X_(self, value):
        self._dmatx[:] = value

    @property
    def dtype(self):
        return self._dmatx.dtype

    @dtype.setter
    def dtype(self, value):
        self._dmatx = self._dmatx.astype(value)
        if self.dtype.kind == 'u' or (self.dtype.kind == 'i' and self.dtype.itemsize < 8):
            logging.warning('special integer dtype may cause na comparison failure')

    @property
    def rownames(self):
        return self._rnames

    @rownames.setter
    def rownames(self, value):
        if isnull(value): self._rnames = na; return
        self._rnames = NamedIndex(value, fixRepeat = self._fixrep)
        if self._rnames.size != self.nrow: raise ValueError('input row names size not match')

    @property
    def colnames(self):
        return self._cnames

    @colnames.setter
    def colnames(self, value):
        if isnull(value): self._cnames = na; return
        self._cnames = NamedIndex(value, fixRepeat = self._fixrep)
        if self._cnames.size != self.ncol: raise ValueError('input column names size not match')

    @property
    def rowindex(self):
        return self._rindex

    @rowindex.setter
    def rowindex(self, value):
        if isnull(value): self._rindex = na; return
        self._rindex = StructuredArray(value)
        if self._rindex.size != 0 and self._rindex.length != self.nrow: raise ValueError('input row index size not match')

    @property
    def colindex(self):
        return self._cindex

    @colindex.setter
    def colindex(self, value):
        if isnull(value): self._cindex = na; return
        self._cindex = StructuredArray(value)
        if self._cindex.size != 0 and self._cindex.length != self.ncol: raise ValueError('input column index size not match')

    @property
    def metadata(self):
        return self._metas

    @property
    def T(self):
        tab = Table(self._dmatx.T, dtype = self.dtype, metadata = self._metas, fixRepeat = self._fixrep)
        tab._rnames, tab._cnames = self._cnames.copy(), self._rnames.copy()
        tab._rindex, tab._cindex = self._cindex.copy(), self._rindex.copy()
        return tab

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
    def fixRepeat(self):
        return self._fixrep

    @fixRepeat.setter
    def fixRepeat(self, value):
        self._fixrep = bool(value)
        if available(self._rnames): self._rnames.fixRepeat = self._fixrep
        if available(self._cnames): self._cnames.fixRepeat = self._fixrep

    # publics
    def append(self, other, axis = 0):
        if not isinstance(other, Table): raise TypeError('unknown input data type')
        if axis == 0:
            if other.ncol != self.ncol: raise IndexError('input table has different number of columns')
            if available(self._cnames) and available(other._cnames) and np.any(other._cnames != self._cnames): raise IndexError('input table has different column names')
            if available(self._cindex) and available(other._cindex) and other._cindex != self._cindex: raise IndexError('input table has different column index')

            tab = Table(np.r_[self._dmatx, other._dmatx], dtype = self.dtype, metadata = self._metas, fixRepeat = self._fixrep)
            if available(self._rnames): tab.rownames = self._rnames + other._rnames
            if available(self._cnames): tab.colnames = self._cnames.copy()
            if available(self._rindex): tab.rowindex = self._rindex + other._rindex
            if available(self._cindex): tab.colindex = self._cindex.copy()
            return tab
        elif axis == 1:
            if other.nrow != self.nrow: raise IndexError('input table has different number of rows')
            if available(self._rnames) and available(other._rnames) and np.any(other._rnames != self._rnames): raise IndexError('input table has different row names')
            if available(self._rindex) and available(other._rindex) and other._rindex != self._rindex: raise IndexError('input table has different row index')

            tab = Table(np.c_[self._dmatx, other._dmatx], dtype = self.dtype, metadata = self._metas, fixRepeat = self._fixrep)
            if available(self._rnames): tab.rownames = self._rnames.copy()
            if available(self._cnames): tab.colnames = self._cnames + other._cnames
            if available(self._rindex): tab.rowindex = self._rindex.copy()
            if available(self._cindex): tab.colindex = self._cindex + other._cindex
            return tab
        else: raise IndexError('unsupported axis [%d]' % axis)

    def insert(self, other, pos = na, axis = 0):
        if not isinstance(other, Table): raise TypeError('unknown input data type')
        if axis == 0:
            if other.ncol != self.ncol: raise IndexError('input table has different number of columns')
            if available(self._cnames) and available(other._cnames) and np.any(other._cnames != self._cnames): raise IndexError('input table has different column names')
            if available(self._cindex) and available(other._cindex) and other._cindex != self._cindex: raise IndexError('input table has different column index')

            if missing(pos): pos = self.nrow
            elif available(self._rnames) and strtype_(pos): pos = self._rnames.idsof(pos)

            tab = Table(np.insert(self._dmatx, pos, other._dmatx, axis = 0), dtype = self.dtype, metadata = self._metas, fixRepeat = self._fixrep)
            if available(self._rnames): tab.rownames = self._rnames.insert(other._rnames, pos) # in case np.inert etc will change array shape
            if available(self._cnames): tab.colnames = self._cnames.copy()
            if available(self._rindex): tab.rowindex = self._rindex.insert(other._rindex, pos)
            if available(self._cindex): tab.colindex = self._cindex.copy()
            return tab
        elif axis == 1:
            if other.nrow != self.nrow: raise IndexError('input table has different number of rows')
            if available(self._rnames) and available(other._rnames) and np.any(other._rnames != self._rnames): raise IndexError('input table has different row names')
            if available(self._rindex) and available(other._rindex) and other._rindex != self._rindex: raise IndexError('input table has different row index')

            if missing(pos): pos = self.ncol
            elif available(self._cnames) and strtype_(pos): pos = self._cnames.idsof(pos)

            tab = Table(np.insert(self._dmatx, pos if listable(pos) else [pos], other._dmatx, axis = 1), dtype = self.dtype, metadata = self._metas, fixRepeat = self._fixrep)
            if available(self._rnames): tab.rownames = self._rnames.copy()
            if available(self._cnames): tab.colnames = self._cnames.insert(other._cnames, pos)
            if available(self._rindex): tab.rowindex = self._rindex.copy()
            if available(self._cindex): tab.colindex = self._cindex.insert(other._cindex, pos)
            return tab
        else: raise IndexError('unsupported axis [%d]' % axis)

    def drop(self, pos, axis = 0):
        if axis == 0:
            if missing(pos): pos = self.nrow
            elif available(self._rnames) and strtype_(pos): pos = self._rnames.idsof(pos)

            tab = Table(np.delete(self._dmatx, pos, axis = 0), dtype = self.dtype, metadata = self._metas, fixRepeat = self._fixrep)
            if available(self._rnames): tab.rownames = self._rnames.drop(pos)
            if available(self._cnames): tab.colnames = self._cnames.copy()
            if available(self._rindex): tab.rowindex = self._rindex.drop(pos)
            if available(self._cindex): tab.colindex = self._cindex.copy()
            return tab
        elif axis == 1:
            if missing(pos): pos = self.ncol
            elif available(self._cnames) and strtype_(pos): pos = self._cnames.idsof(pos)

            tab = Table(np.delete(self._dmatx, pos, axis = 1), dtype = self.dtype, metadata = self._metas, fixRepeat = self._fixrep)
            if available(self._rnames): tab.rownames = self._rnames.copy()
            if available(self._cnames): tab.colnames = self._cnames.drop(pos)
            if available(self._rindex): tab.rowindex = self._rindex.copy()
            if available(self._cindex): tab.colindex = self._cindex.drop(pos)
            return tab
        else: raise IndexError('unsupported axis [%d]' % axis)

    def copy(self):
        tab = Table(self._dmatx, dtype = self.dtype, metadata = self._metas, fixRepeat = self._fixrep)
        tab._rnames, tab._cnames = self._rnames.copy(), self._cnames.copy()
        tab._rindex, tab._cindex = self._rindex.copy(), self._cindex.copy()
        return tab

    def astype(self, dtype):
        ds = self.copy()
        ds.dtype = dtype
        return ds

    def tolist(self, transpose = False, withindex = False):
        smtx = [['#'] + list(optional(self._cnames, np.arange(self.ncol)))] + \
               [[rn] + list(ln) for rn, ln in zip(optional(self._rnames, np.arange(self.nrow)), self._dmatx)]

        if withindex:
            if available(self._rindex):
                ridx = smap(zip(*[['<%s>' % n] + list(v) for n, v in zip(self._rindex.names, self._rindex.series)]), list)
                smtx = [ri + sl for ri, sl in zip(ridx, smtx)]
            if available(self._cindex):
                cidx = smap([['<%s>' % n] + list(v) for n, v in zip(self._cindex.names, self._cindex.series)], list)
                smtx = [[''] * len(optional(self._rindex, [])) + ci for ci in cidx] + smtx

        if transpose: smtx = zip(*smtx)
        return smtx

    def tostr(self, delimiter = ',', transpose = False, withindex = False):
        rlns = self._toStrList(delimiter = delimiter, transpose = transpose, withindex = withindex)
        rlns = ['[' + rlns[0]] + \
               [' ' + ln for ln in rlns[1:]]
        return join(rlns, '\n') + ']'


    @classmethod
    def fromsarray(cls, array, dtype = na, rowindex = na, colindex = na):
        if missing(rowindex) or missing(colindex):
            if '#' not in array: raise ValueError('Unknown array format')
            colindex, rowindex = smap(np.where(array == '#'), itemgetter(0))
        ridx = StructuredArray.fromsarray(array[colindex:,:rowindex].T) if rowindex > 0 else na
        cidx = StructuredArray.fromsarray(array[:colindex,rowindex:])   if colindex > 0 else na
        array = array[colindex:,rowindex:]

        cnam = array[0,1:]
        if np.all(cnam == np.arange(cnam.shape[0]).astype(str)): cnam = na
        rnam = array[1:,0]
        if np.all(rnam == np.arange(rnam.shape[0]).astype(str)): rnam = na
        array = array[1:,1:]

        if missing(dtype): dtype = type(autoeval(array[0,0]))
        if dtype in (NAType, NoneType): logging.warning('invalid data type detected')

        return Table(array, dtype = dtype, rownames = rnam, colnames = cnam, rowindex = ridx, colindex = cidx)

    def tosarray(self, withindex = True):
        return np.array(self.tolist(transpose = False, withindex = withindex), dtype = str)

    @classmethod
    def loadcsv(cls, fname, dtype = na, delimiter = ',', transposed = False, rowindex = na, colindex = na):
        idm = np.array(tablePortal.load(fname, delimiter = delimiter))
        if transposed: idm = idm.T
        return cls.fromsarray(idm, dtype = dtype, rowindex = rowindex, colindex = colindex)

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

        rnam = hdf.root.RowNames.read() if hasattr(hdf.root, 'RowNames') else na
        cnam = hdf.root.ColNames.read() if hasattr(hdf.root, 'ColNames') else na
        ridx = StructuredArray.fromhtable(hdf.root.RowIndex) if hasattr(hdf.root, 'RowIndex') else na
        cidx = StructuredArray.fromhtable(hdf.root.ColIndex) if hasattr(hdf.root, 'ColIndex') else na

        hdf.close()
        return Table(darr, metadata = meta, rownames = rnam, colnames = cnam, rowindex = ridx, colindex = cidx)

    def savehdf(self, fname, compression = 0):
        checkOutputFile(fname)
        hdf = ptb.open_file(fname, mode = 'w', filters = ptb.Filters(compression))

        darr = hdf.create_array(hdf.root, 'DataMatx', self._dmatx)
        for k,v in self._metas.items(): setattr(darr.attrs, k, v)

        if available(self._rnames): hdf.create_array(hdf.root, 'RowNames', np.array(self._rnames))
        if available(self._cnames): hdf.create_array(hdf.root, 'ColNames', np.array(self._cnames))
        if available(self._rindex) and self._rindex.size > 0: self._rindex.tohtable(hdf.root, 'RowIndex')
        if available(self._cindex) and self._cindex.size > 0: self._cindex.tohtable(hdf.root, 'ColIndex')

        hdf.close()
        return os.path.isfile(fname)

    @classmethod
    def loadrdata(cls, fname, dname, rowindex = na, colindex = na, dataTransposed = True):
        from kagami.wrappers.rWrapper import RWrapper as rw

        checkInputFile(fname)
        rw.r.load(fname)

        dm, rn, cn = rw.r[dname], rw.run('rownames(%s)' % dname), rw.run('colnames(%s)' % dname) # stupid numpy conversion
        if dataTransposed: dm, rn, cn = dm.T, cn, rn

        tabl = Table(dm, metadata = {'_rdata_file_name': fname})
        if rn is not rw.null: tabl.rownames = rn
        if cn is not rw.null: tabl.colnames = cn

        def _parseidx(iname):
            idx = rw.r[iname]
            return zip(idx.dtype.names, zip(*idx))
        if available(rowindex): tabl.rowindex = _parseidx(rowindex)
        if available(colindex): tabl.colindex = _parseidx(colindex)

        return tabl

    def saverdata(self, fname, dname = 'data', rowindex = 'row.index', colindex = 'col.index', dataTranspose = True):
        from kagami.wrappers.rWrapper import RWrapper as rw

        checkOutputFile(fname)

        dm, rn, cn = (self._dmatx,   self._rnames, self._cnames) if not dataTranspose else \
                     (self._dmatx.T, self._cnames, self._rnames)

        dmtx = rw.asMatrix(dm)
        if available(rn): dmtx.rownames = rw.asVector(rn)
        if available(cn): dmtx.colnames = rw.asVector(cn)
        rw.assign(dmtx, dname)

        if available(self._rindex): rw.assign(rw.r['data.frame'](**{k: rw.asVector(self._rindex[k]) for k in self._rindex.names}), rowindex)
        if available(self._cindex): rw.assign(rw.r['data.frame'](**{k: rw.asVector(self._cindex[k]) for k in self._cindex.names}), colindex)

        vnames = [dname] + ([rowindex] if available(self._rindex) else []) + ([colindex] if available(self._cindex) else [])
        rw.run('save(%s, file = "%s")' % (join(vnames, ','), fname)) # avoid bug in rw.save

        return os.path.isfile(fname)
