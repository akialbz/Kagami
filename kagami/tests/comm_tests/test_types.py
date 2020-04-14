#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
test_core.py

author(s): Albert (aki) Zhou
added: 11-14-2018

"""


import numpy as np
import pickle as pkl
from collections import defaultdict, OrderedDict
from kagami.comm import *


def test_none():
    assert missing(None) and not missing('') and not missing(False) and not missing(np.nan) and not missing([])
    assert available('') and available(False) and available(np.nan) and available([]) and not available(None)
    assert optional('a', 'b') == 'a' and optional(None, 'b') == 'b' and optional(None, np.nan) is np.nan

def test_autoeval():
    assert autoeval('11') == 11 and np.isclose(autoeval(' 12.3'), 12.3)
    assert autoeval('a ') == 'a ' and autoeval(' abs  ') != abs and eval(' abs  ') == abs
    assert autoeval('  [1,2,3]') == [1,2,3]
    assert autoeval('na') is None and autoeval('n/a') is None and autoeval('NA') is None and autoeval('N/A') is None
    assert autoeval('None') is None and autoeval('nONe') is  None

def test_types():
    assert isstring('abc') and isstring(u'def') and isstring(np.array(['ghi'])[0])
    assert not isstring(1) and not isstring(False)

    assert ismapping({}) and ismapping(defaultdict(list)) and ismapping(OrderedDict())
    assert not ismapping([]) and not ismapping(()) and not ismapping(iter([]))

    assert hashable('a') and hashable(())
    assert not hashable([]) and not hashable(slice(None))

    assert iterable([]) and iterable(np.arange(3)) and iterable({}) and iterable(iter(range(5))) and not iterable('abc')
    assert listable([]) and listable(np.arange(3)) and not listable({}) and not listable(iter(range(5))) and not listable('abc')

def test_metadata():
    meta = Metadata(a = 1, b = 2)
    assert meta == Metadata([('a', 1), ('b', 2)])

    assert meta.a == 1 and meta.b == 2
    assert meta['a'] == 1 and meta['b'] == 2
    assert meta.get('c', 3) == 3

    assert 'a' in meta and not 'c' in meta
    assert set(meta.keys()) == {'a', 'b'} and set(meta.values()) == {1, 2}

    meta.a = 4
    meta.c = 5
    assert set(meta.items()) == {('a', 4), ('b', 2), ('c', 5)}

    del meta.c
    assert set(meta.items()) == {('a', 4), ('b', 2)}

    assert pkl.loads(pkl.dumps(meta)) == meta
