#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
table

author(s): Albert (aki) Zhou
added: 02-18-2017

"""


from __future__ import annotations

import logging, os, re
import numpy as np
import tables as ptb
import pandas as pd
from typing import Iterable, Sequence, Mapping, Union, Optional, Any
from pathlib import Path
from kagami.comm import ll, optional, missing, available, isstring, iterable, listable, checkany, paste, imap, smap, collapse, checkInputFile, checkOutputFile, Metadata
from kagami.portals import tablePortal
from .coreType import CoreType, Indices, Indices2D
from .namedIndex import NamedIndex
from .structArray import StructuredArray
try:
    from kagami.wrappers.rWrapper import RWrapper as rw
except ImportError as e: rw = None


__all__ = ['Table']


# table class
_copy = lambda x: None if x is None else x.copy()

class Table(CoreType):
    __slots__ = ('_dmatx', '_rnames', '_cnames', '_rindex', '_cindex', '_metas', '_memmap')

    def __init__(self, X: Iterable[Iterable], *, dtype: Optional[Union[str, type, np.ndarray.dtype]] = None,
                 rownames: Optional[Union[Iterable[str], NamedIndex]] = None, rowindex: Optional[Union[Iterable, Mapping, np.ndarray, StructuredArray]] = None,
                 colnames: Optional[Union[Iterable[str], NamedIndex]] = None, colindex: Optional[Union[Iterable, Mapping, np.ndarray, StructuredArray]] = None,
                 metadata: Optional[Union[Sequence, Mapping]] = None, memmap: Optional[Union[str, Path]] = None):
        if not isinstance(X, np.ndarray): X = smap(X, ll)
        self._dmatx = np.array(X, dtype = dtype) # make a copy
        if self._dmatx.ndim != 2: raise ValueError('input data is not a 2-dimensional matrix')

        self._memmap = None
        if available(memmap): self.offload(memmap)

        self._rnames = self._cnames = None
        self.rows_ = rownames
        self.cols_ = colnames

        self._rindex = self._cindex = None
        self.ridx_ = rowindex
        self.cidx_ = colindex

        self._metas = Metadata(optional(metadata, ()))

    # privates
    @staticmethod
    def _mapids(ids, names):
        if isinstance(ids, NamedIndex):
            ids = np.array(ids)
        else:
            if not listable(ids): ids = [ids]
            if not checkany(ids, isstring): return ids
        if missing(names): raise KeyError('table names not set')
        return names.idsof(ids, safe = False)

    def _parseids(self, idx, axis = None, mapslice = True):
        if missing(axis):
            rids, cids = (idx, slice(None)) if not isinstance(idx, tuple) else \
                         (idx[0], slice(None)) if len(idx) == 1 else idx
        else:
            if isinstance(idx, tuple): raise IndexError('too many dimensions for array')
            if axis not in (0, 1): raise IndexError('invalid axis value')
            rids, cids = (idx, slice(None)) if axis == 0 else (slice(None), idx)

        def _wrap(ids, num, names):
            if ids is None: return slice(None) if not mapslice else np.arange(num)
            if isinstance(ids, slice): return ids if not mapslice else np.arange(num)[ids]
            return self._mapids(ids, names)

        rids = _wrap(rids, self.nrow, self._rnames)
        cids = _wrap(cids, self.ncol, self._cnames)
        return rids, cids

    def _parsevals(self, value):
        if isinstance(value, Table): return value._dmatx.astype(self.dtype)
        if isinstance(value, np.ndarray): return value.astype(self.dtype)
        if not iterable(value): return value

        value = ll(value)
        if not iterable(value[0]): return np.asarray(value, dtype = self.dtype)

        value = np.asarray(value if isinstance(value, np.ndarray) and value.ndim == 2 else smap(value, ll), dtype = self.dtype)
        return value

    def _tostrlns(self, delimiter, *, transpose = False, withindex = True, strinkrows = 15, strinkcols = 10):
        def _fmt(mtx, rnam, cnam, ridx, cidx):
            nr, nc = mtx.shape

            if missing(rnam): rnam = smap(range(nr), lambda x: f'[{x}]')
            if missing(cnam): cnam = smap(range(nc), lambda x: f'[{x}]')

            _sln  = lambda x,sr,hd,tl,rp: (smap(x[:hd],str) + [rp] + smap(x[tl:],str)) if sr else smap(x, str)
            _scol = lambda x: _sln(x, nc > strinkcols, 3, -1, ' ... ')
            _srow = lambda x: _sln(x, nr > strinkrows, 5, -3, '')

            slns = [_scol(cnam)] + \
                  ([_scol(ln) for ln in mtx] if nr <= strinkrows else
                  ([_scol(ln) for ln in mtx[:5]] + [_scol([' ... ... '] + [''] * (nc-1))] + [_scol(ln) for ln in mtx[-3:]]))
            slns = [['#'] + slns[0]] + [[n] + ln for n,ln in zip(_srow(rnam), slns[1:])]

            nri = ridx.size if available(ridx) else 0
            nci = cidx.size if available(cidx) else 0

            if nci > 0: slns = [[f'<{k}>'] + _scol(cidx[k]) for k in cidx.names] + slns
            if nri > 0:
                sidx = [[''] * nci + [f'<{k}>'] + _srow(ridx[k]) for k in ridx.names]
                slns = [list(ix) + ln for ix,ln in zip(zip(*sidx), slns)]

            def _sfmt(lns, pos):
                size = max(collapse(smap(lns, lambda x: smap(x[pos], lambda v: len(v) if v not in (' ... ', ' ... ... ') else 0)))) + 1
                for ln in lns: ln[pos] = smap(ln[pos], lambda x: '{0:>{1}s}'.format(x, size) if x != ' ... ' else x)
                return lns

            if nri > 0: slns = _sfmt(slns, slice(None,nri))
            slns = _sfmt(slns, slice(nri,nri+1))
            slns = _sfmt(slns, slice(nri+1,None))

            return smap(slns, lambda ln: paste(ln, sep = delimiter))

        sdm = _fmt(self._dmatx, self._rnames, self._cnames, self._rindex if withindex else None, self._cindex if withindex  else None) if not transpose else \
              _fmt(self._dmatx.T, self._cnames, self._rnames, self._cindex if withindex else None, self._rindex if withindex else None)
        return sdm

    # built-ins
    def __getitem__(self, item):
        return self.take(item, axis = None)

    def __setitem__(self, key, value):
        self.put(key, value, axis = None, inline = True)

    def __delitem__(self, key):
        self.delete(key, axis = None, inline = True)

    def __iter__(self):
        return imap(self._dmatx, np.array)

    def __contains__(self, item):
        return item in self._dmatx

    def __len__(self):
        return self.size

    def __eq__(self, other):
        if isinstance(other, Table):
            equ = self.shape == other.shape and np.all(self._dmatx == other._dmatx)
            if available(self._rnames) and available(other._rnames): equ = equ and np.all(self._rnames == other._rnames)
            if available(self._cnames) and available(other._cnames): equ = equ and np.all(self._cnames == other._cnames)
            if available(self._rindex) and available(other._rindex): equ = equ and self._rindex == other._rindex
            if available(self._cindex) and available(other._cindex): equ = equ and self._cindex == other._cindex
        else:
            equ = self._dmatx == other
        return equ

    def __lt__(self, other):
        return self._dmatx < other

    def __gt__(self, other):
        return self._dmatx > other

    def __le__(self, other):
        return self._dmatx <= other

    def __ge__(self, other):
        return self._dmatx >= other

    def __str__(self):
        return self.tostring(delimiter = ',', transpose = False, withindex = True)

    def __repr__(self):
        rlns = self._tostrlns(delimiter = ',')
        rlns = ['Table([' + rlns[0]] + \
               ['       ' + ln for ln in rlns[1:]]
        return paste(rlns, sep = '\n') + f'], size = ({self.nrow}, {self.ncol}))'

    # for numpy
    def __array__(self, dtype = None):
        return np.asarray(self._dmatx, dtype = dtype)

    def __array_wrap__(self, arr):
        return Table(arr)

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
    def rownames(self):
        return _copy(self._rnames)

    @property
    def rows_(self):
        return self._rnames

    @rows_.setter
    def rows_(self, value):
        if missing(value): self._rnames = None; return
        self._rnames = NamedIndex(value)
        if self._rnames.size != self.nrow: raise ValueError('input row names size not match')

    @property
    def colnames(self):
        return _copy(self._cnames)

    @property
    def cols_(self):
        return self._cnames

    @cols_.setter
    def cols_(self, value):
        if missing(value): self._cnames = None; return
        self._cnames = NamedIndex(value)
        if self._cnames.size != self.ncol: raise ValueError('input column names size not match')

    @property
    def rowindex(self):
        return _copy(self._rindex)

    @property
    def ridx_(self):
        return self._rindex

    @ridx_.setter
    def ridx_(self, value):
        if missing(value): self._rindex = None; return
        self._rindex = StructuredArray(value)
        if self._rindex.size != 0 and self._rindex.length != self.nrow: raise ValueError('input row index size not match')

    @property
    def colindex(self):
        return _copy(self._cindex)

    @ property
    def cidx_(self):
        return self._cindex

    @cidx_.setter
    def cidx_(self, value):
        if missing(value): self._cindex = None; return
        self._cindex = StructuredArray(value)
        if self._cindex.size != 0 and self._cindex.length != self.ncol: raise ValueError('input column index size not match')

    @property
    def dtype(self):
        return self._dmatx.dtype

    @dtype.setter
    def dtype(self, value):
        self._dmatx = self._dmatx.astype(value)

    @property
    def metadata(self):
        return self._metas

    @property
    def T(self):
        tab = Table(self._dmatx.T, metadata = self._metas)
        tab._rnames, tab._cnames = _copy(self._cnames), _copy(self._rnames)
        tab._rindex, tab._cindex = _copy(self._cindex), _copy(self._rindex)
        return tab

    @property
    def size(self):
        return self._dmatx.shape[0]

    @property
    def shape(self):
        return self._dmatx.shape

    @property
    def nrow(self):
        return self.shape[0]

    @property
    def ncol(self):
        return self.shape[1]

    @property
    def ndim(self):
        return 2

    @property
    def df(self):
        return self.todataframe(multidx = False)

     # publics
    def take(self, pos: Indices2D, axis: Optional[int] = 0) -> Table:
        rids, cids = self._parseids(pos, axis = axis)
        ntab = Table(
            self._dmatx[np.ix_(rids, cids)], dtype = self.dtype,
            rownames = self._rnames[rids] if available(self._rnames) else None,
            colnames = self._cnames[cids] if available(self._cnames) else None,
            rowindex = self._rindex[:,rids] if available(self._rindex) else None,
            colindex = self._cindex[:,cids] if available(self._cindex) else None,
            metadata = self._metas,
        )
        return ntab

    def put(self, pos: Indices2D, value: Any, axis: Optional[int] = 0, inline: bool = False) -> Table:
        ntab = self if inline else self.copy()
        vals = self._parsevals(value)

        if isinstance(pos, np.ndarray) and pos.shape == ntab.shape and pos.dtype.kind == 'b':
            ntab._dmatx[pos] = vals # for e.g. tab[tab == 0] = 1
        else:
            rids, cids = self._parseids(pos, axis = axis)
            ntab._dmatx[np.ix_(rids, cids)] = vals
            if isinstance(value, Table):
                if available(ntab._rnames): ntab._rnames[rids] = value._rnames
                if available(ntab._cnames): ntab._cnames[cids] = value._cnames
                if available(ntab._rindex): ntab._rindex[:,rids] = value._rindex
                if available(ntab._cindex): ntab._cindex[:,cids] = value._cindex
        return ntab

    def append(self, value: Table, axis: int = 0, inline: bool = False) -> Table:
        return self.insert(None, value = value, axis = axis, inline = inline)

    def insert(self, pos: Indices, value: Table, axis: int = 0, inline: bool = False) -> Table:
        if not isinstance(value, Table): raise TypeError('unknown input data type')

        ntab = self if inline else self.copy()
        if axis == 0:
            if value.ncol != ntab.ncol: raise IndexError('input table has different number of columns')
            if available(pos): pos = self._mapids(pos, self._rnames)
            ntab._dmatx = np.vstack([ntab._dmatx, value._dmatx.astype(ntab.dtype)]) if missing(pos) else \
                          np.insert(ntab._dmatx, pos, value._dmatx.astype(ntab.dtype), axis = 0)
            if available(ntab._cnames) and available(value._cnames) and np.any(value._cnames != ntab._cnames): raise IndexError('input table has different column names')
            if available(ntab._cindex) and available(value._cindex) and value._cindex != ntab._cindex: raise IndexError('input table has different column index')
            if available(ntab._rnames): ntab._rnames.insert(pos, value._rnames, inline = True)
            if available(ntab._rindex): ntab._rindex.insert(pos, value._rindex, inline = True)
        elif axis == 1:
            if value.nrow != ntab.nrow: raise IndexError('input table has different number of rows')
            if available(pos): pos = self._mapids(pos, self._cnames)
            ntab._dmatx = np.hstack([ntab._dmatx, value._dmatx.astype(ntab.dtype)]) if missing(pos) else \
                          np.insert(ntab._dmatx, pos, value._dmatx.astype(ntab.dtype), axis = 1)
            if available(ntab._rnames) and available(value._rnames) and np.any(value._rnames != ntab._rnames): raise IndexError('input table has different row names')
            if available(ntab._rindex) and available(value._rindex) and value._rindex != self._rindex: raise IndexError('input table has different row index')
            if available(ntab._cnames): ntab._cnames.insert(pos, value._cnames, inline = True)
            if available(ntab._cindex): ntab._cindex.insert(pos, value._cindex, inline = True)
        else: raise IndexError(f'unsupported axis [{axis}]')

        return ntab

    def delete(self, pos: Indices2D, axis: Optional[int] = 0, inline: bool = False) -> Table:
        ntab = self if inline else self.copy()

        rids, cids = self._parseids(pos, axis = axis, mapslice = False)
        rlic = isinstance(rids, slice) and rids == slice(None)
        clic = isinstance(cids, slice) and cids == slice(None)

        if rlic and clic:
            ntab._dmatx = np.array([], dtype = ntab.dtype).reshape((0,0))
            if available(ntab._rnames): ntab._rnames.delete(rids, inline = True)
            if available(ntab._rindex): ntab._rindex.delete(rids, axis = 1, inline = True)
            if available(ntab._cnames): ntab._cnames.delete(cids, inline = True)
            if available(ntab._cindex): ntab._cindex.delete(cids, axis = 1, inline = True)
        elif rlic and not clic:
            if not isinstance(cids, slice) and len(cids) == 1: cids = cids[0] # fix strange numpy.delete behaviour...
            ntab._dmatx = np.delete(ntab._dmatx, cids, axis = 1)
            if available(ntab._cnames): ntab._cnames.delete(cids, inline = True)
            if available(ntab._cindex): ntab._cindex.delete(cids, axis = 1, inline = True)
        elif clic and not rlic:
            if not isinstance(rids, slice) and len(rids) == 1: rids = rids[0]
            ntab._dmatx = np.delete(ntab._dmatx, rids, axis = 0)
            if available(ntab._rnames): ntab._rnames.delete(rids, inline = True)
            if available(ntab._rindex): ntab._rindex.delete(rids, axis = 1, inline = True)
        else: raise IndexError('unable to delete portion of the table')

        return ntab

    def tolist(self) -> Any:
        return self._dmatx.tolist()

    def tostring(self, delimiter: str = ',', transpose: bool = False, withindex: bool = False) -> str:
        rlns = self._tostrlns(delimiter = delimiter, transpose = transpose, withindex = withindex)
        rlns = ['[' + rlns[0]] + \
               [' ' + ln for ln in rlns[1:]]
        return paste(rlns, sep = '\n') + ']'

    def todataframe(self, idname: str = 'id', multidx: bool = False) -> pd.DataFrame:
        rnam = np.asarray(self._rnames) if available(self._rnames) else np.array(smap(range(self.nrow), lambda x: f'[{x}]'))
        cnam = np.asarray(self._cnames) if available(self._cnames) else np.array(smap(range(self.ncol), lambda x: f'[{x}]'))

        df = pd.DataFrame(self._dmatx.copy())
        def _pack_mulindex(nams, index):
            ns,vs = (index.names.tolist(), index.arrays) if available(index) else ([],[])
            return pd.MultiIndex.from_arrays(vs + [nams], names = ns + [idname])
        df.index   = rnam if (not multidx) and missing(self._rindex) else _pack_mulindex(rnam, self._rindex)
        df.columns = cnam if (not multidx) and missing(self._cindex) else _pack_mulindex(cnam, self._cindex)

        return df

    def copy(self) -> Table:
        return self.astype()

    def astype(self, dtype: Optional[Union[str, np.dtype, type]] = None) -> Table:
        ntab = Table(self._dmatx, dtype = optional(dtype, self.dtype), metadata = self._metas)
        ntab._rnames, ntab._cnames = _copy(self._rnames), _copy(self._cnames)
        ntab._rindex, ntab._cindex = _copy(self._rindex), _copy(self._cindex)
        return ntab

    # memory offload
    def onload(self, removefile: bool = False) -> Table:
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
        mdmatx = np.memmap(fname, dtype = self.dtype, mode = 'w+', shape = self.shape)
        mdmatx[:] = self._dmatx
        self._dmatx = mdmatx

        self._memmap = Metadata(file = Path(fname), dtype = self.dtype, shape = self.shape)
        return self

    # portals
    @classmethod
    def fromsarray(cls, array: np.ndarray, dtype: Optional[Union[str, type, np.ndarray.dtype]] = None, headerpos: Optional[Union[Sequence[int], np.ndarray]] = None) -> Table:
        _r = re.compile('#<::([<>|]?[biufcmMOSUV]\\d*)::>')
        _findt = lambda x: (lambda v: v[0] if len(v) > 0 else '')(_r.findall(x))

        if missing(headerpos):
            mtab = np.vectorize(_findt)(array[:100,:100])
            dpos = np.c_[np.where(mtab != '')]
            if dpos.shape[0] >= 2: raise ValueError('string array has multiple headers')
            if dpos.shape[0] == 0: raise ValueError('string array has no header in the first 100 rows / cols')
            headerpos = dpos[0]
        rids, cids = headerpos

        if missing(dtype):
            dtype = _findt(array[rids,cids])
            if dtype == '': raise ValueError('unknown array data type')

        ridx = StructuredArray.fromsarray(array[rids:,:cids].T) if cids > 0 else None
        cidx = StructuredArray.fromsarray(array[:rids,cids:])   if rids > 0 else None

        rnam = array[rids+1:,cids]
        if np.all(rnam == smap(range(rnam.shape[0]), lambda x: f'[{x}]')): rnam = None
        cnam = array[rids,cids+1:]
        if np.all(cnam == smap(range(cnam.shape[0]), lambda x: f'[{x}]')): cnam = None

        dmtx = array[rids+1:,cids+1:]
        return Table(dmtx, dtype = dtype, rownames = rnam, colnames = cnam, rowindex = ridx, colindex = cidx)

    def tosarray(self, withindex: bool = True, withdtype: bool = True) -> np.ndarray:
        rnam = np.asarray(self._rnames) if available(self._rnames) else np.array(smap(range(self.nrow), lambda x: f'[{x}]'))
        cnam = np.asarray(self._cnames) if available(self._cnames) else np.array(smap(range(self.ncol), lambda x: f'[{x}]'))
        smtx = np.vstack([
            np.hstack([f'#<::{self.dtype.str}::>' if withdtype else '#', cnam]),
            np.hstack([rnam.reshape((-1,1)), np.asarray(self._dmatx, dtype = str)])
        ])
        if not withindex: return smtx

        if available(self._rindex):
            ridx = self._rindex.tosarray(withdtype = withdtype)
            smtx = np.hstack([ridx.T, smtx])
        if available(self._cindex):
            cidx = self._cindex.tosarray(withdtype = withdtype)
            if available(self._rindex): cidx = np.hstack([np.tile([''], (self._cindex.size, self._rindex.size)), cidx])
            smtx = np.vstack([cidx, smtx])
        return smtx

    @classmethod
    def loadcsv(cls,  fname: Union[str, Path], *, delimiter: str = ',', transposed: bool = False,
                dtype: Optional[Union[str, type, np.ndarray.dtype]] = None, headerpos: Optional[Union[Sequence[int], np.ndarray]] = None) -> Table:
        idm = np.array(tablePortal.load(fname, delimiter = delimiter))
        if transposed: idm = idm.T
        return cls.fromsarray(idm, dtype = dtype, headerpos = headerpos)

    def savecsv(self, fname: Union[str, Path], *, delimiter: str = ',', transpose: bool = False, withindex: bool = True) -> bool:
        odm = self.tosarray(withindex = withindex)
        if transpose: odm = odm.T
        tablePortal.save(odm, fname, delimiter = delimiter)
        return os.path.isfile(fname)

    @classmethod
    def loadhdf(cls, fname: Union[str, Path]) -> Table:
        checkInputFile(fname)
        hdf = ptb.open_file(fname, mode = 'r')

        darr = hdf.root.DataMatx.read()
        if darr.dtype.kind == 'S': darr = np.array(darr, dtype = str)
        meta = [(n, getattr(hdf.root.DataMatx.attrs, n)) for n in hdf.root.DataMatx.attrs._f_list('user')]

        rnam = np.array(hdf.root.RowNames.read(), dtype = str) if hasattr(hdf.root, 'RowNames') else None
        cnam = np.array(hdf.root.ColNames.read(), dtype = str) if hasattr(hdf.root, 'ColNames') else None
        ridx = StructuredArray.fromhtable(hdf.root.RowIndex) if hasattr(hdf.root, 'RowIndex') else None
        cidx = StructuredArray.fromhtable(hdf.root.ColIndex) if hasattr(hdf.root, 'ColIndex') else None

        hdf.close()
        return Table(darr, rownames = rnam, colnames = cnam, rowindex = ridx, colindex = cidx, metadata = meta)

    def savehdf(self, fname: Union[str, Path], compression: int = 0) -> bool:
        checkOutputFile(fname)
        hdf = ptb.open_file(fname, mode = 'w', filters = ptb.Filters(compression))

        darr = hdf.create_array(hdf.root, 'DataMatx', self._dmatx)
        for k,v in self._metas.items(): setattr(darr.attrs, k, v)

        if available(self._rnames): hdf.create_array(hdf.root, 'RowNames', np.array(self._rnames))
        if available(self._cnames): hdf.create_array(hdf.root, 'ColNames', np.array(self._cnames))
        if available(self._rindex): self._rindex.tohtable(hdf.root, 'RowIndex')
        if available(self._cindex): self._cindex.tohtable(hdf.root, 'ColIndex')

        hdf.close()
        return os.path.isfile(fname)

    @classmethod
    def loadrdata(cls, fname: Union[str, Path], dataobj: str, *,
                  ridxobj: Optional[str] = None, cidxobj: Optional[str] = None, transposed: bool = True) -> Table:
        if missing(rw): raise RuntimeError('RWrapper not available for this installation')
        checkInputFile(fname)
        rw.r.load(fname)

        # import pdb; pdb.set_trace()

        dm, rn, cn = np.array(rw.r[dataobj]), rw.run(f'rownames({dataobj})'), rw.run(f'colnames({dataobj})') # stupid numpy conversion
        rn = None if rn is rw.null else np.array(rn)
        cn = None if cn is rw.null else np.array(cn)

        def _parseidx(iname):
            idx = rw.robj.numpy2ri.rpy2py_data_frame(rw.r[iname])
            return zip(idx.dtype.names, zip(*idx))
        ri = _parseidx(ridxobj) if available(ridxobj) else None
        ci = _parseidx(cidxobj) if available(cidxobj) else None

        if transposed: dm, rn, cn, ri, ci = dm.T, cn, rn, ci, ri
        ntab = Table(dm, rownames = rn, colnames = cn, rowindex = ri, colindex = ci)
        return ntab

    def saverdata(self, fname, *, dataobj: str = 'data.matrix',
                  ridxobj: Optional[str] = 'row.index', cidxobj: Optional[str] = 'col.index', transpose: bool = True) -> bool:
        if missing(rw): raise RuntimeError('RWrapper not available for this installation')
        checkOutputFile(fname)

        dm, rn, cn, ri, ci = (self._dmatx,   self._rnames, self._cnames, self._rindex, self._cindex) if not transpose else \
                             (self._dmatx.T, self._cnames, self._rnames, self._cindex, self._rindex)

        dmtx = rw.asMatrix(dm, rownames = rn, colnames = cn)
        rw.assign(dmtx, dataobj)

        if available(ri): rw.assign(rw.r['data.frame'](**{k: rw.asVector(v) for k,v in ri.fields}), ridxobj)
        if available(ci): rw.assign(rw.r['data.frame'](**{k: rw.asVector(v) for k,v in ci.fields}), cidxobj)

        vnames = [dataobj] + ([ridxobj] if available(ri) else []) + ([cidxobj] if available(ci) else [])
        rw.run(f'save({paste(vnames, sep = ",")}, file = "{fname}")') # avoid bug in rw.save
        return os.path.isfile(fname)
