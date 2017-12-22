#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
rWrapper: wrapper for R language

author(s): Albert
origin: 12-19-2017

"""


import numpy as np
import rpy2.robjects as robj
import rpy2.robjects.numpy2ri as np2ri
from ..prelim import NA, hasvalue, optional


class RWrapper(object):
    def __init__(self, libraries = NA):
        np2ri.activate() # enable numpy <-> R object conversions
        robj.r('Sys.setenv(LANG = "en")')
        if hasvalue(libraries): self.library(*libraries)

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
        return np.array(getattr(robj.r, func)(*args, **kwargs))
