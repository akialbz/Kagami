#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
etc

author(s): Albert (aki) Zhou
origin: 06-07-2016

"""


import logging
from ast import literal_eval
from collections import Iterable, Mapping, Hashable
from types import GeneratorType
from null import na


__all__ = [
    'autoeval', 'isstring', 'mappable', 'hashable', 'iterable', 'listable', 'isiterator', 'checkall', 'checkany', 'peek'
]


# auto eval
def autoeval(x):
    if not isstring(x): logging.warning('unable to eval non-string value [%s]' % str(x))
    v = x.strip()
    if v in ('na', 'n/a', 'NA', 'N/A'): return na
    try: return literal_eval(v)
    except (ValueError, SyntaxError): return x


# iterable
isstring = lambda x: isinstance(x, basestring)
mappable = lambda x: isinstance(x, Mapping)
hashable = lambda x: isinstance(x, Hashable) and not isinstance(x, slice)
iterable = lambda x: isinstance(x, Iterable)
listable = lambda x: iterable(x) and not isstring(x)
isiterator = lambda x: iterable(x) and hasattr(x, '__iter__') and hasattr(x, 'next') # use __next__ for py3


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
           (default, rest) if len(rest) == 0 else (rest[0], rest[1:])
