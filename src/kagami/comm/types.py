#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
dtype

author(s): Albert (aki) Zhou
added: 06-07-2016

"""


import numpy as np
from typing import Any, Iterable, Sequence, Mapping, Hashable, Callable, Optional
from ast import literal_eval


__all__ = ['missing', 'available', 'optional', 'autoeval', 'isstring', 'ismapping', 'hashable', 'iterable', 'listable', 'Metadata']


# null type
missing:   Callable[[Optional[Any]], bool] = lambda x: x is None
available: Callable[[Optional[Any]], bool] = lambda x: x is not None
optional:  Callable[[Optional[Any], Any], Any]  = lambda x, default: x if available(x) else default


# auto eval
def autoeval(x: str) -> Any:
    v = x.strip()
    if v.lower() in ('na', 'n/a', 'nan', 'none'): return None
    try: return literal_eval(v)
    except (ValueError, SyntaxError): return x


# type and checking
isstring:  Callable[[Any], bool] = lambda x: isinstance(x, str)
ismapping: Callable[[Any], bool] = lambda x: isinstance(x, Mapping)
hashable:  Callable[[Any], bool] = lambda x: isinstance(x, Hashable)
iterable:  Callable[[Any], bool] = lambda x: isinstance(x, Iterable) and not isinstance(x, (str, bytes))
listable:  Callable[[Any], bool] = lambda x: isinstance(x, (Sequence, np.ndarray)) and not isinstance(x, (str, bytes))


# metadata type
class Metadata(dict):
    __slots__ = ()

    def __getattr__(self, item):
        return self[item] if item in self else super().__getattribute__(item)

    def __setattr__(self, item, value):
        if item not in self.__slots__: self[item] = value
        else: super().__setattr__(item, value)

    def __delattr__(self, item):
        if item in self: del self[item]
        else: super().__delattr__(item)

    def __getstate__(self):
        return {k: getattr(self, k) for k in self.__slots__}

    def __setstate__(self, dct):
        for k in [v for v in dct if v in self.__slots__]: setattr(self, k, dct[k])

