#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
rWrapper

author(s): Albert (aki) Zhou
added: 12-19-2017

"""


import warnings
import numpy as np
try:
    import rpy2.robjects as robj
    import rpy2.robjects.packages as rpkg
    from rpy2.rinterface_lib.embedded import RRuntimeError
    from rpy2.robjects import numpy2ri
    if numpy2ri.original_converter is None: numpy2ri.activate()
except ImportError:
    raise ImportError('rWrapper requires r environment and rpy2 package')
from typing import Iterable, Union, Optional, Any
from kagami.comm import l, ll, missing, available, smap, pickmap, iterable


__all__ = ['RWrapper']


class RWrapper: # pragma: no cover
    # rpy2 delegates
    robj = robj
    null = robj.NULL
    r = robj.r
    RuntimeError = RRuntimeError

    def __init__(self, *libraries: Union[str, Iterable[str]], mute: bool = True):
        self.library(*libraries, mute = mute)

    # methods
    @staticmethod
    def library(*args: Union[str, Iterable[str]], mute: bool = True) -> None:
        if len(args) == 1 and iterable(args[0]): args = args[0]
        with warnings.catch_warnings():
            if mute: warnings.filterwarnings('ignore')
            for pkg in args: rpkg.importr(pkg, suppress_messages = mute)

    @staticmethod
    def installed(library: str) -> bool:
        return rpkg.isinstalled(library)

    @staticmethod
    def clean() -> None:
        return robj.r('rm(list = ls())')

    @staticmethod
    def asVector(val: Iterable, names: Optional[Iterable] = None) -> robj.Vector:
        val = np.asarray(ll(val))
        vect = {
            'i': robj.IntVector, 'u': robj.IntVector,
            'f': robj.FloatVector,
            'b': robj.BoolVector,
            'S': robj.StrVector, 'U': robj.StrVector,
        }.get(val.dtype.kind, lambda x: None)(val)
        if missing(vect): raise TypeError(f'unknown vector type [{val.dtype.kind}]')
        if available(names): vect.names = robj.StrVector(np.asarray(ll(names), dtype = str))
        return vect

    @staticmethod
    def asMatrix(val: Iterable[Iterable], nrow: Optional[int] = None, ncol: Optional[int] = None,
                 rownames: Optional[Iterable] = None, colnames: Optional[Iterable] = None) -> robj.Matrix:
        if not (isinstance(val, np.ndarray) and val.ndim == 2): val = np.asarray(smap(val,ll))
        if missing(nrow) and missing(ncol): nrow, ncol = val.shape
        matx = robj.r.matrix(val, nrow = nrow, ncol = ncol)
        if available(rownames): matx.rownames = robj.StrVector(np.asarray(ll(rownames), dtype = str))
        if available(colnames): matx.colnames = robj.StrVector(np.asarray(ll(colnames), dtype = str))
        return matx

    @staticmethod
    def assign(val: Any, name: str) -> None:
        return robj.r.assign(name, val)

    @staticmethod
    def apply(func: str, *args: Any, **kwargs: Any) -> Any:
        args = pickmap(args, missing, robj.NULL)
        kwargs = {k: (robj.NULL if missing(v) else v) for k,v in kwargs.items()}
        return getattr(robj.r, func)(*args, **kwargs)

    @staticmethod
    def run(cmd: str) -> Any:
        return robj.r(cmd)
