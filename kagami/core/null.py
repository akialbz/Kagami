#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
optvalue

author(s): Albert (aki) Zhou
origin: 06-07-2016

"""


import logging
import numpy as np
from math import isnan
from collections import Iterable


__all__ = ['na', 'NAType', 'missing', 'available', 'optional', 'isnull', 'isna']


# optional type, never use it directly
class _NA(object):
    __slots__ = ()
    char_     = ''
    integer_  = -9223372036854775808
    float_    = float('nan')
    bool_     = False

    # comparison
    @classmethod
    def __eq__(cls, other): return isinstance(other, _NA)
    @classmethod
    def __ne__(cls, other): return not cls.__eq__(other)

    # type conversion, not reversible
    @classmethod
    def __str__(cls): return cls.char_
    @classmethod
    def __int__(cls): return cls.integer_
    @classmethod
    def __long__(cls): return cls.integer_
    @classmethod
    def __float__(cls): return cls.float_
    @classmethod
    def __nonzero__(cls): return cls.bool_

    # for printing
    @classmethod
    def __repr__(cls): return 'N/A'

    # for pickling
    def __getstate__(self):
        return {k: getattr(self, k) for k in self.__slots__}

    def __setstate__(self, dct):
        for k in [v for v in dct.keys() if v in self.__slots__]: setattr(self, k, dct[k])

    # copy
    def copy(self): return self

na = _NA() # fixed object
NAType = _NA # alias type

# works on variable
missing = lambda x: isinstance(x, _NA)
available = lambda x: not missing(x)
optional = lambda x, default: x if available(x) else default
isnull = lambda x: missing(x) or x is None

# works on array
def isna(x):
    if isinstance(x, basestring) or not isinstance(x, Iterable): return missing(x)

    if isinstance(x, np.ndarray) and x.dtype.kind != 'O':
        dt = x.dtype.kind
        if dt not in ('f', 'i'): logging.warning('unsafe na checking for ndarray dtype [%s]', dt)
        return np.isnan(x) if dt == 'f' else x == na.integer_ if dt == 'i' else np.zeros_like(x, dtype = bool)
    else:
        return np.array([isnan(v) if isinstance(v, float) else v == na.integer_ if isinstance(v, int) else v == na for v in list(x)])

