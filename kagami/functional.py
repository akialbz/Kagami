#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
functional

author(s): Albert (aki) Zhou
origin: 06-07-2016

"""


import functools
from multiprocessing import Pool, cpu_count
from multiprocessing.pool import ThreadPool
from kagami.core import NA, hasvalue, optional, listable, checkall


# partial & composition
def partial(func, *args, **kwargs):
    pfunc = functools.partial(func, *args, **kwargs)
    functools.update_wrapper(pfunc, func)  # partial with __name__ & __doc__ etc copied
    return pfunc

def compose(*funcs):
    if len(funcs) <= 1: raise ValueError('too few functions for composition')
    def _appl(fs, v):
        r = fs[0](v)
        return r if len(fs) == 1 else _appl(fs[1:], r)
    return partial(_appl, funcs)


# mappers
def smap(x, func):
    return map(func, x)

def _mmap(x, func, ptype, nps):
    if nps is None or nps >= cpu_count(): nps = cpu_count() - 1 # in case dead lock
    mpool = ptype(processes = nps)
    jobs = [mpool.apply_async(func, (p,)) for p in x]
    mpool.close()
    mpool.join()
    return [j.get() for j in jobs]

def tmap(x, func, nthreads = NA):
    return _mmap(x, func, ThreadPool, optional(nthreads, None))

def pmap(x, func, nprocs = NA):
    return _mmap(x, func, Pool, optional(nprocs, None))

def call(x, funcs, nthreads = NA, nprocs = NA, collect = NA):
    if not listable(x): raise TypeError('source in not listable')
    if len(funcs) == 0: raise ValueError('too few functions for piping')
    if hasvalue(nthreads) and hasvalue(nprocs): raise ValueError('cannot use multithreading and multiprocssing as the same time')
    if hasvalue(collect) and not callable(collect): raise TypeError('collector is not callable')

    _map = smap if checkall((nprocs, nthreads), NA) else \
           partial(tmap, nthreads = nthreads) if hasvalue(nthreads) else \
           partial(pmap, nprocs = nprocs)
    res = reduce(lambda v, f: _map(v, f), funcs, x)
    return collect(res) if hasvalue(collect) else res


# functions
def unpack(func):
    def _wrap(x): return func(*x)
    return _wrap

def pick(x, cond):
    _check = cond if callable(cond) else (lambda x: x == cond)
    return filter(_check, x)

def pickmap(x, cond, func):
    _check = cond if callable(cond) else (lambda x: x == cond)
    _replc = func if callable(func) else (lambda: func)
    return smap(x, lambda v: _replc(v) if _check(v) else v)

def drop(x, cond):
    _check = cond if callable(cond) else (lambda x: x == cond)
    return filter(lambda v: not _check(v), x)

def fold(x, func, init = NA):
    return reduce(func, x, initializer = optional(init, None))

