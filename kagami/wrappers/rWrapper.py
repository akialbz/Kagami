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
    import rpy2.robjects.numpy2ri as np2ri
    from rpy2.robjects import NULL
    from rpy2.rinterface import RRuntimeError
except ImportError:
    raise ImportError('rWrapper requires r environment and rpy2 package')
from kagami.core import na, isnull, missing, pickmap


np2ri.activate()  # enable numpy <-> R conversions
robj.r('Sys.setenv(LANG = "en")')

class RWrapper(object): # pragma: no cover
    # rpy2 delegates
    null = NULL
    robj = robj
    r = robj.r

    def __init__(self, *libraries, **kwargs):
        self.library(*libraries, **kwargs)

    # methods
    @staticmethod
    def clean():
        return robj.r('rm(list = ls())')

    @staticmethod
    def library(*args, **kwargs):
        mute = kwargs.pop('mute', False)
        if mute:
            with warnings.catch_warnings():
                warnings.filterwarnings('ignore')
                for pkg in args: robj.r.library(pkg, quietly = True)
        else:
            for pkg in args: robj.r.library(pkg, quietly = True)

    @staticmethod
    def asVector(val):
        val = np.array(val)
        _pack = {
            'i': robj.IntVector, 'u': robj.IntVector,
            'f': robj.FloatVector,
            'b': robj.BoolVector,
            'S': robj.StrVector, 'U': robj.StrVector,
        }.get(val.dtype.kind, na)
        if missing(_pack): raise TypeError('unknown vector type [%s]' % val.dtype.kind)
        return _pack(val)

    @staticmethod
    def asMatrix(val, nrow = na, ncol = na):
        val = np.array(val)
        if missing(nrow) and missing(ncol): nrow, ncol = val.shape
        return robj.r.matrix(val, nrow = nrow, ncol = ncol)

    @staticmethod
    def assign(val, name):
        return robj.r.assign(name, val)

    @staticmethod
    def apply(func, *args, **kwargs):
        args = pickmap(args, isnull, NULL)
        kwargs = {k: (NULL if v is None or missing(v) else v) for k,v in kwargs.items()}
        return getattr(robj.r, func)(*args, **kwargs)

    @staticmethod
    def run(cmd):
        return robj.r(cmd)
