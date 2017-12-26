#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
functional: functional programming

author(s): Albert (aki) Zhou
origin: 06-07-2016

"""


import logging, functools
from copy import deepcopy
from prelim import NA, hasvalue, iterable, peek


# lambdas
def lraise(cond, err):
    if cond: raise err

def lassert(cond, msg):
    assert cond, msg

def lassign(dist, index = NA, attr = NA, value = NA, update = NA):
    if not (hasvalue(index) or hasvalue(attr)): raise IndexError('index and attribute cannot be both None')
    if not (hasvalue(value) or hasvalue(update)): raise ValueError('value and setter cannot be both None')

    if hasvalue(index): dist[index] = value if hasvalue(value) else update(dist[index])
    else: setattr(dist, attr, value if hasvalue(value) else update(getattr(dist, attr)))

    return dist


# pipeline & element
class element(object):
    na = object() # DO NOT use NA

    def __init__(self, func):
        self._func = func
        functools.wraps(self._func)(self)

    def __ror__(self, other):
        def _generator():
            if not iterable(other): raise TypeError('source is not iterable')
            for obj in other:
                ret = self._func(obj)
                if ret is not element.na: yield ret
        return _generator()

def pipe(p, c = lambda x: x):
    if not iterable(p): raise TypeError('source in not iterable')
    if not callable(c): raise TypeError('collector is not callable')
    return c([e for e in p]) # keep "[]" to return a list rather than a generator

def do(func):
    @element
    def _wrap(x):
        return func(x)
    return _wrap

def put(func):
    @element
    def _wrap(x):
        func(deepcopy(x))
        return x
    return _wrap

def unpack(func):
    def _wrap(x):
        if not iterable(x): raise TypeError('parameter is not iterable')
        return func(*x)
    return _wrap

@element
def skip(x):
    return x

_passed = lambda x, cond: cond(x) if callable(cond) else (cond == x)

def pick(cond):
    return do(lambda x: x if _passed(x, cond) else element.na)

def drop(cond):
    return do(lambda x: x if not _passed(x, cond) else element.na)

def check(cond):
    return do(lambda x: _passed(x, cond))

def echo(msg, level = logging.INFO):
    return put(lambda x: logging.log(level, msg(x) if callable(msg) else msg))


# partial & composition
def partial(func, *args, **kwargs):
    pfunc = functools.partial(func, *args, **kwargs)
    functools.update_wrapper(pfunc, func)  # partial with __name__ & __doc__ etc copied
    return pfunc

def composite(*funcs):
    if not len(funcs) > 1: raise ValueError('too few functions for composition')
    def _appl(fs, v):
        r = fs[0](v)
        return r if len(fs) == 1 else _appl(fs[1:], r)
    return partial(_appl, funcs)


# structure
def iterate(itr, func, bkcond = lambda x: False): # return: last result (on break), NA
    if not iterable(itr): raise TypeError('source is not iterable')
    if not callable(bkcond): raise TypeError('break condition is not callable')

    def _iterate(x, r):
        head, rest = peek(x, NA)
        if head is NA: return r
        nr = func(head)
        return nr if bkcond(nr) else _iterate(rest, nr)
    return _iterate(itr, None)

def loop(itr, func, bkcond = lambda x: False): # return: all results (before break), []
    if not iterable(itr): raise TypeError('source is not iterable')
    if not callable(bkcond): raise TypeError('break condition is not callable')

    def _loop(x, res):
        head, rest = peek(x, NA)
        if head is NA: return res
        r = func(head)
        return res if bkcond(r) else _loop(rest, res + [r])
    return _loop(itr, [])

