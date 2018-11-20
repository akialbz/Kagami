#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
prelim

author(s): Albert (aki) Zhou
origin: 06-07-2016

"""


import logging
from ast import literal_eval
from collections import Iterable, Mapping, Hashable
from types import GeneratorType


__all__ = [
    'NA', 'NAType', 'isna', 'isnull', 'hasvalue', 'optional',
    'Metadata', 'autoeval', 'isstring', 'mappable', 'hashable', 'iterable', 'listable', 'isiterator',
    'checkall', 'checkany', 'peek',
]


# optional type
class _NA(object):
    def __nonzero__(self): return False
    def __eq__(self, other): return isinstance(other, _NA)
    def __ne__(self, other): return not self.__eq__(other)
    def __float__(self): return float('nan')
    def __str__(self): return 'NA'
    def __repr__(self): return self.__str__()
    def copy(self): return self
NA = _NA() # fixed object
NAType = _NA # alias type

isna = lambda x: isinstance(x, _NA)
isnull = lambda x: isna(x) or (x is None)
hasvalue = lambda x: not isna(x)
optional = lambda x, default: x if hasvalue(x) else default


# metadata type
class Metadata(dict):
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        super(Metadata, self).__init__(*args, **kwargs)

    def __getattr__(self, item):
        return self[item] if self.has_key(item) else super(Metadata, self).__getattribute__(item)

    def __setattr__(self, item, value):
        if item not in self.__slots__: self[item] = value
        else: super(Metadata, self).__setattr__(item, value)

    def __delattr__(self, item):
        if self.has_key(item): del self[item]
        else: super(Metadata, self).__delattr__(item)

    def __getstate__(self):
        return {k: getattr(self, k) for k in self.__slots__}

    def __setstate__(self, dct):
        for k in filter(lambda x: x in self.__slots__, dct.keys()): setattr(self, k, dct[k])


# auto eval
def autoeval(x):
    if not isstring(x): logging.warning('unable to eval non-string value [%s]' % str(x))
    v = x.strip()
    if v == 'NA': return NA
    try: return literal_eval(v)
    except (ValueError, SyntaxError): return x


# iterable
isstring = lambda x: isinstance(x, basestring)
mappable = lambda x: isinstance(x, Mapping)
hashable = lambda x: isinstance(x, Hashable) and not isinstance(x, slice)
iterable = lambda x: isinstance(x, Iterable)
listable = lambda x: iterable(x) and not isstring(x)
isiterator = lambda x: iterable(x) and hasattr(x, '__iter__') and hasattr(x, 'next') # __next__ for py3


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
    return (next(rest, default), rest) if isinstance(rest, GeneratorType) or isiterator(rest) else \
           (default, rest) if (not rest) else (rest[0], rest[1:])
