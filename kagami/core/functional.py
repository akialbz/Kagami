#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
functional

author(s): Albert (aki) Zhou
origin: 06-07-2016

"""


import functools
import numpy as np
from multiprocessing import Pool, cpu_count
from multiprocessing.pool import ThreadPool
from operator import itemgetter
from null import na, available, missing
from etc import listable, peek


__all__ = [
    'partial', 'compose', 'unpack', 'smap', 'tmap', 'pmap', 'cmap', 'call', 'pick', 'pickmap', 'drop', 'fold', 'collapse'
]


# partial & composition
def partial(func, *args, **kwargs):
    pfunc = functools.partial(func, *args, **kwargs)
    functools.update_wrapper(pfunc, func)  # partial with __name__ & __doc__ etc copied
    return pfunc

def compose(*funcs):
    if len(funcs) < 1: raise ValueError('too few functions for composition')
    def _appl(fs, v):
        r = fs[0](v)
        return r if len(fs) == 1 else _appl(fs[1:], r)
    return partial(_appl, funcs)


# mappers
def unpack(func):
    def _wrap(x): return func(*x)
    return _wrap

def smap(x, func):
    return map(func, x)

def _mmap(x, func, ptype, nps):
    if missing(nps) or nps >= cpu_count(): nps = cpu_count() - 1 # in case dead lock
    mpool = ptype(processes = nps)
    jobs = [mpool.apply_async(func, (p,)) for p in x]
    mpool.close()
    mpool.join()
    return [j.get() for j in jobs]

def tmap(x, func, nthreads = na):
    return _mmap(x, func, ThreadPool, nthreads)

def pmap(x, func, nprocs = na):
    return _mmap(x, func, Pool, nprocs)

def cmap(x, func, nchunks = na):
    if missing(nchunks): nchunks = cpu_count() - 1
    if nchunks > len(x): nchunks = len(x)
    ids = smap(np.array_split(np.arange(len(x)), nchunks), lambda i: i if len(i) > 1 else [i])
    pms = smap(ids, lambda i: itemgetter(*i)(x))
    _func = lambda ps: smap(ps, func)
    return collapse(tmap(pms, _func, nchunks))

def call(x, funcs, nthreads = na, nprocs = na, collect = na):
    if not listable(x): raise TypeError('source in not listable')
    if len(funcs) == 0: raise ValueError('too few functions for piping')
    if available(nthreads) and available(nprocs): raise ValueError('cannot use multithreading and multiprocssing as the same time')
    if available(collect) and not callable(collect): raise TypeError('collector is not callable')

    _map = smap if missing(nprocs) and missing(nthreads) else \
           partial(tmap, nthreads = nthreads) if available(nthreads) else \
           partial(pmap, nprocs = nprocs)
    res = reduce(lambda v, f: _map(v, f), funcs, x)
    return collect(res) if available(collect) else res


# utils
def pick(x, cond):
    _check = cond if callable(cond) else (lambda v: v == cond)
    return filter(_check, x)

def pickmap(x, cond, func):
    _check = cond if callable(cond) else (lambda v: v == cond)
    _replc = func if callable(func) else (lambda v: func)
    return smap(x, lambda v: _replc(v) if _check(v) else v)

def drop(x, cond):
    _check = cond if callable(cond) else (lambda v: v == cond)
    return filter(lambda v: not _check(v), x)

def fold(x, func, init = na):
    if missing(init): init, x = peek(x)
    return reduce(func, x, init)

def collapse(x, init = na):
    return fold(x, lambda a,b: a+b, init = init)
