#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
prelim: preliminary functions

author(s): Albert Zhou
origin: 06-07-2016

"""


from collections import Iterable, Mapping
from types import GeneratorType


# optional type
class _NA(object):
    def __nonzero__(self): return False
NA = _NA() # fixed object

hasvalue = lambda x: x is not NA
optional = lambda x, default: x if hasvalue(x) else default


# iterable
iterable = lambda x: isinstance(x, Iterable)
listable = lambda x: iterable(x) and type(x) not in (str, unicode)
mappable = lambda x: isinstance(x, Mapping)

def peek(rest, default = None):
    if not iterable(rest): raise ValueError('source is not iterable')
    if isinstance(rest, GeneratorType): return next(rest, default), rest
    else: return (default, rest) if (not rest) else (rest[0], rest[1:])


# check
def checkall(itr, cond):
    if not iterable(itr): raise ValueError('source is not iterable')
    for x in itr:
        istrue = cond(x)
        if not istrue: return False
    return True

def checkany(itr, cond):
    if not iterable(itr): raise ValueError('source is not iterable')
    for x in itr:
        istrue = cond(x)
        if istrue: return True
    return False
