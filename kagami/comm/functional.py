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
from .types import optional, missing, listable


__all__ = [
    'partial', 'compose', 'unpack', 'imap', 'smap', 'tmap', 'pmap', 'cmap',
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

def smap(x: Iterable, *funcs: Callable) -> List:
    # remove depencency of map function to avoid error shallowing
    # check: https://stackoverflow.com/questions/37362373/is-stopiteration-raised-in-the-mapping-function-of-python-3-map-handled-incorr
    return functools.reduce(lambda v,f: [f(p) for p in v], funcs, x)

def imap(x: Iterable, *funcs: Callable) -> Iterator:
    return iter(smap(x, *funcs))

def _mmap(x, func, ptype, nps):
    mpool = ptype(processes = nps)
    jobs = [mpool.apply_async(func, (p,)) for p in x]
    mpool.close()
    mpool.join()
    return [j.get() for j in jobs]

def tmap(x: Iterable, *funcs: Callable, nthreads: Optional[int] = None) -> List:
    return l(functools.reduce(functools.partial(_mmap, ptype = ThreadPool, nps = optional(nthreads, cpu_count())), funcs, x))

def pmap(x: Iterable, *funcs: Callable, nprocs: Optional[int] = None) -> List:
    return l(functools.reduce(functools.partial(_mmap, ptype = Pool, nps = optional(nprocs, cpu_count()-1)), funcs, x))

def cmap(x: Union[Collection, np.ndarray], *funcs: Callable, nchunks: Optional[int] = None) -> List:
    xln = len(x)
    chk = min(optional(nchunks, cpu_count()), xln)

    ids = np.array_split(np.arange(xln), chk)
    pms = smap(ids, lambda i: (lambda v: [v] if len(i) == 1 else v)(itemgetter(*i)(x)))
    _func = lambda ps: smap(ps, *funcs)

    return collapse(tmap(pms, _func, nthreads = min(cpu_count(), chk)))


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
