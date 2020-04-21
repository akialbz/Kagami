#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
functional

author(s): Albert (aki) Zhou
added: 06-07-2016

"""


import functools
import numpy as np
from typing import Any, Iterable, Collection, List, Iterator, Callable, Optional, Union
from multiprocessing import cpu_count
from multiprocessing.pool import Pool, ThreadPool
from operator import itemgetter
from .types import available, optional, missing, listable


__all__ = [
    'partial', 'compose', 'unpack', 'imap', 'smap', 'tmap', 'pmap', 'cmap', 'call',
    'l', 'll', 'lzip', 'pick', 'pickmap', 'drop', 'fold', 'collapse',
]


# partial & composition
def partial(func: Callable, *args: Any, **kwargs: Any) -> Callable:
    pfunc = functools.partial(func, *args, **kwargs)
    functools.update_wrapper(pfunc, func)  # partial with __name__ & __doc__ etc copied
    return pfunc

def compose(*funcs: Callable) -> Callable:
    if len(funcs) < 2: raise ValueError('too few functions for composition')
    def _appl(fs, v):
        r, fs = fs[0](v), fs[1:]
        return r if len(fs) == 0 else _appl(fs, r)
    return partial(_appl, funcs)


# mappers
def unpack(func: Callable) -> Callable:
    def _wrap(x): return func(*x)
    return _wrap

def imap(x: Iterable, func: Callable) -> Iterator:
    return map(func, x)

def smap(x: Iterable, func: Callable) -> List:
    return l(map(func, x))

def _mmap(x, func, ptype, nps):
    mpool = ptype(processes = nps)
    jobs = [mpool.apply_async(func, (p,)) for p in x]
    mpool.close()
    mpool.join()
    return [j.get() for j in jobs]

def tmap(x: Iterable, func: Callable, nthreads: Optional[int] = None) -> List:
    return _mmap(x, func, ThreadPool, optional(nthreads, cpu_count() * 10))

def pmap(x: Iterable, func: Callable, nprocs: Optional[int] = None) -> List:
    return _mmap(x, func, Pool, optional(nprocs, cpu_count()-1))

def cmap(x: Union[Collection, np.ndarray], func: Callable, nchunks: Optional[int] = None) -> List:
    if missing(nchunks): nchunks = cpu_count() - 1
    x = ll(x)
    xln = len(x)
    ids = pickmap(np.array_split(np.arange(xln), min(nchunks, xln)), lambda i: len(i) == 1, lambda i: [i])
    pms = smap(ids, lambda i: itemgetter(*i)(x))
    _func = lambda ps: smap(ps, func)
    return collapse(tmap(pms, _func, nchunks))

def call(x: Iterable, funcs: Collection[Callable], nthreads: Optional[int] = None, nprocs: Optional[int] = None) -> List:
    if len(funcs) == 0: raise ValueError('too few functions for piping')
    if available(nthreads) and available(nprocs): raise ValueError('cannot use multithreading and multiprocssing as the same time')
    _map = smap if missing(nprocs) and missing(nthreads) else \
           partial(tmap, nthreads = nthreads) if available(nthreads) else \
           partial(pmap, nprocs = nprocs)
    res = functools.reduce(_map, funcs, x)
    return res


# utils
l = list # fuck the stupid iterator

def ll(x: Any) -> List:
    return x if listable(x) else list(x)

def lzip(*args: Any) -> List:
    return l(zip(*args))

def pick(x: Iterable, cond: Union[Callable, Any]) -> List:
    _check = cond if callable(cond) else (lambda v: v == cond)
    return l(filter(_check, x))

def pickmap(x: Iterable, cond: Union[Callable, Any], func: Callable) -> List:
    _check = cond if callable(cond) else (lambda v: v == cond)
    _replc = func if callable(func) else (lambda v: func)
    return [_replc(v) if _check(v) else v for v in x]

def drop(x: Iterable, cond: Union[Callable, Any]) -> List:
    _check = cond if callable(cond) else (lambda v: v == cond)
    return [v for v in x if not _check(v)]

def fold(x: Iterable, func: Callable, init: Optional[Any] = None) -> Any:
    if not isinstance(x, Iterator): x = iter(x)
    if missing(init): init, x = next(x), x
    return functools.reduce(func, x, init)

def collapse(x: Iterable, init: Optional[Any] = None) -> Any:
    return fold(x, lambda a,b: a+b, init = init)
