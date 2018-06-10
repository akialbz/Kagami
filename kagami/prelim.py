#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
prelim: preliminary functions

author(s): Albert (aki) Zhou
origin: 06-07-2016

"""


from collections import Iterable, Mapping
from types import GeneratorType


# optional type
class _NA(object):
    def __nonzero__(self): return False
    def __eq__(self, other): return isinstance(other, _NA)
    def __str__(self): return 'NA'
    def __repr__(self): return self.__str__()
NA = _NA() # fixed object

isna = lambda x: isinstance(x, _NA)
hasvalue = lambda x: not isna(x)
optional = lambda x, default: x if hasvalue(x) else default

# iterable
iterable = lambda x: isinstance(x, Iterable)
listable = lambda x: iterable(x) and not isinstance(x, (str, unicode))
mappable = lambda x: isinstance(x, Mapping)

def peek(rest, default = None):
    if not iterable(rest): raise ValueError('source is not iterable')
    return (next(rest, default), rest) if isinstance(rest, GeneratorType) else \
           (default, rest) if (not rest) else (rest[0], rest[1:])


# check
def checkall(itr, cond):
    if not iterable(itr): raise ValueError('source is not iterable')
    for x in itr:
        if not cond(x):return False
    return True

def checkany(itr, cond):
    if not iterable(itr): raise ValueError('source is not iterable')
    for x in itr:
        if cond(x): return True
    return False
