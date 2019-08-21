#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
rWrapper

author(s): Albert (aki) Zhou
origin: 12-19-2017

"""


import warnings
import numpy as np
try:
    import rpy2.robjects as robj
    import rpy2.robjects.packages as rpkg
    from rpy2.rinterface import RRuntimeError
    from rpy2.robjects import numpy2ri
except ImportError:
    raise ImportError('rWrapper requires r environment and rpy2 package')
from typing import Iterable, Any
from kagami.common import missing, pickmap


__all__ = ['RWrapper']



class RWrapper: # pragma: no cover
    # rpy2 delegates
    null = robj.NULL
    robj = robj
    r = robj.r
    RuntimeError = RRuntimeError

    def __init__(self, *libraries: str, mute: bool = True):
        self.library(*libraries, mute = mute)
        if numpy2ri.original_converter is None: numpy2ri.activate()

    # methods
    @staticmethod
    def library(*args: str, mute: bool = True) -> None:
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
    def asVector(val: Iterable) -> robj.Vector:
        val = np.array(val)
        _pack = {
            'i': robj.IntVector, 'u': robj.IntVector,
            'f': robj.FloatVector,
            'b': robj.BoolVector,
            'S': robj.StrVector, 'U': robj.StrVector,
        }.get(val.dtype.kind, None)
        if missing(_pack): raise TypeError('unknown vector type [%s]' % val.dtype.kind)
        return _pack(val)

    @staticmethod
    def asMatrix(val: Iterable[Iterable], nrow = None, ncol = None) -> robj.Matrix:
        val = np.array(val)
        if missing(nrow) and missing(ncol): nrow, ncol = val.shape
        return robj.r.matrix(val, nrow = nrow, ncol = ncol)

    @staticmethod
    def apply(func: str, *args: Any, **kwargs: Any) -> Any:
        args = pickmap(args, missing, robj.NULL)
        kwargs = {k: (robj.NULL if missing(v) else v) for k,v in kwargs.items()}
        return getattr(robj.r, func)(*args, **kwargs)

    @staticmethod
    def run(cmd: str) -> Any:
        return robj.r(cmd)
