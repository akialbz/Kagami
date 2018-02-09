#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
rWrapper: wrapper for R language

author(s): Albert (aki) Zhou
origin: 12-19-2017

"""


import numpy as np
import rpy2.robjects as robj
import rpy2.robjects.numpy2ri as np2ri
from rpy2.robjects import NULL
from ..prelim import NA, optional, isna


class RWrapper(object):
    def __init__(self, *libraries):
        np2ri.activate() # enable numpy <-> R object conversions
        robj.r('Sys.setenv(LANG = "en")')
        self.library(*libraries)

    # methods
    @staticmethod
    def clean():
        return robj.r('rm(list = ls())')

    @staticmethod
    def library(*args):
        return robj.r.library(*args)

    @staticmethod
    def assign(val, name, dtype = NA):
        return robj.r.assign(name, np.array(val, dtype = optional(dtype, None)))

    @staticmethod
    def apply(func, *args, **kwargs):
        args = map(lambda x: NULL if x is None or isna(x) else x, args)
        kwargs = {k: (NULL if v is None or isna(v) else v) for k,v in kwargs.items()}
        return getattr(robj.r, func)(*args, **kwargs)

    @staticmethod
    def run(cmd):
        return robj.r(cmd)
