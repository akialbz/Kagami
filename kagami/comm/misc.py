#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
misc

author(s): Albert (aki) Zhou
added: 06-07-2016

"""


import numpy as np
from typing import Tuple, Any, Iterable, Collection, Callable, Union
from .types import iterable


__all__ = [
    'T', 'F', 'paste', 'checkany', 'checkall', 'validarg', 'unique'
]


# R-like components
T = True
F = False

def paste(*args: Any, sep: str = '') -> str:
    if len(args) == 1 and iterable(args[0]): args = args[0]
    return sep.join([str(v) for v in args])


# handy snippets
def checkall(itr: Iterable, cond: Union[Callable, Any]) -> bool:
    _check = cond if callable(cond) else (lambda x: x is None) if cond is None else (lambda x: x == cond)
    for val in itr:
        if not _check(val): return False
    return True

def checkany(itr: Iterable, cond: Union[Callable, Any]) -> bool:
    _check = cond if callable(cond) else (lambda x: x is None) if cond is None else (lambda x: x == cond)
    for val in itr:
        if _check(val): return True
    return False

def validarg(arg: Any, valids: Union[Collection, np.ndarray]) -> Any:
    if arg not in valids: raise ValueError(f'[{arg}] is not a valid argument value')
    return arg

def unique(itr: Iterable, return_counts: bool = False) -> Union[np.ndarray, Tuple[np.ndarray,np.ndarray]]:
    itr = np.asarray(itr)
    _,uid,*cnt = np.unique(itr, return_index = True, return_counts = return_counts)
    sid = np.argsort(uid)
    return itr[uid[sid]] if len(cnt) == 0 else (itr[uid[sid]], cnt[0][sid])
