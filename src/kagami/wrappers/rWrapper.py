#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
rWrapper

author(s): Albert (aki) Zhou
added: 12-19-2017

"""


import warnings, numpy as np
from kagami.comm import optional
try:
    import rpy2.robjects as robj
    import rpy2.robjects.packages as rpkg
    from rpy2.rinterface_lib.embedded import RRuntimeError
    from rpy2.robjects import numpy2ri
except ImportError:
    raise ImportError('rWrapper requires r environment and rpy2 package')
from typing import Iterable, Union, Optional, Any
from kagami.comm import ll, missing, available, smap, pickmap, iterable


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
        vect = numpy2ri.numpy2rpy(val)
        if available(names):
            names = np.asarray(ll(names), dtype = str)
            if len(names) != len(val): raise ValueError('values and names size not match')
            vect.names = robj.StrVector(names)
        return vect

    @staticmethod
    def asMatrix(val: Iterable[Iterable], nrow: Optional[int] = None, ncol: Optional[int] = None,
                 rownames: Optional[Iterable] = None, colnames: Optional[Iterable] = None) -> robj.Matrix:
        if not isinstance(val, np.ndarray): val = np.array(smap(val,ll))
        if not val.ndim == 2: raise ValueError('input data is not a 2-dimensional matrix')

        if available(nrow) or available(ncol): val = val.reshape((optional(nrow,-1), optional(ncol,-1)))
        nrow, ncol = val.shape
        matx = robj.r.matrix(numpy2ri.numpy2rpy(val), nrow = nrow, ncol = ncol)

        def _wrap_nams(nams, nval):
            nams = np.asarray(ll(nams), dtype = str)
            if len(nams) != nval: raise ValueError('values and names size not match')
            return robj.StrVector(nams)
        if available(rownames): matx.rownames = _wrap_nams(rownames, nrow)
        if available(colnames): matx.colnames = _wrap_nams(colnames, ncol)
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
