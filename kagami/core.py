#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
prelim

author(s): Albert (aki) Zhou
origin: 06-07-2016

"""


from ast import literal_eval
from collections import Iterable, Mapping, Hashable
from types import GeneratorType


# optional type
class _NA(object):
    def __nonzero__(self): return False
    def __eq__(self, other): return isinstance(other, _NA)
    def __float__(self): return float('nan')
    def __str__(self): return 'NA'
    def __repr__(self): return self.__str__()
NA = _NA() # fixed object
NAType = _NA # alias type

isna = lambda x: isinstance(x, _NA)
hasvalue = lambda x: not isna(x)
optional = lambda x, default: x if hasvalue(x) else default


# auto eval
def autoeval(x):
    if x == 'NA': return NA
    try: return literal_eval(x)
    except (ValueError, SyntaxError): return str(x)


# iterable
isstring = lambda x: isinstance(x, basestring)
mappable = lambda x: isinstance(x, Mapping)
hashable = lambda x: isinstance(x, Hashable) and not isinstance(x, slice)
iterable = lambda x: isinstance(x, Iterable)
listable = lambda x: iterable(x) and not isstring(x)


# check
def checkall(itr, cond):
    if not listable(itr): raise ValueError('source is not listable')
    _check = cond if callable(cond) else (lambda x: x == cond)
    for val in itr:
        if not _check(val): return False
    return True

def checkany(itr, cond):
    if not listable(itr): raise ValueError('source is not listable')
    _check = cond if callable(cond) else (lambda x: x == cond)
    for val in itr:
        if _check(val): return True
    return False


# listable oprtations
def peek(rest, default = None):
    if not listable(rest): raise ValueError('source is not listable')
    return (next(rest, default), rest) if isinstance(rest, GeneratorType) else \
           (default, rest) if (not rest) else (rest[0], rest[1:])

def partition(itr, pos, *funcs):
    if not listable(itr): raise ValueError('source is not listable')
    pos = list(pos)
    parts = [itr[slice(st,ed)] for st,ed in zip([None] + pos, pos + [None])]
    if funcs == (): return parts
    if len(funcs) != len(parts): raise ValueError('partitions and funcs have different lengths')
    if checkany(funcs, lambda x: not callable(x)): raise TypeError('not all funcs are callable')
    return map(lambda x: x[0](x[1]), zip(funcs, parts))
