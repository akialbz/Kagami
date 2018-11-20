#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
test_core.py

author(s): Albert (aki) Zhou
origin: 11-14-2018

"""


import cPickle as cp
import numpy as np
from copy import deepcopy
from collections import defaultdict, OrderedDict
from kagami.core import *


def test_NA():
    assert NA == deepcopy(NA)
    assert NA != '' and NA is not None
    assert isinstance(NA, NAType)

    assert isna(NA)
    assert not isna(None)
    assert isnull(NA) and isnull(None)
    assert not isnull('')
    assert hasvalue('') and hasvalue(False) and hasvalue(np.nan) and hasvalue(())
    assert optional('a', 'b') == 'a' and optional(None, 'b') is None and optional(NA, 'b') == 'b'

def test_metadata():
    meta = Metadata(a = 1, b = 2)
    assert meta == Metadata([('a', 1), ('b', 2)])

    assert meta.a == 1 and meta.b == 2
    assert meta['a'] == 1 and meta['b'] == 2
    assert meta.get('c', 3) == 3

    assert meta.has_key('a') and not meta.has_key('c')
    assert 'a' in meta and not 'c' in meta
    assert set(meta.keys()) == {'a', 'b'} and set(meta.values()) == {1, 2}

    meta.a = 4
    meta.c = 5
    assert set(meta.items()) == {('a', 4), ('b', 2), ('c', 5)}

    assert cp.loads(cp.dumps(meta)) == meta

def test_autoeval():
    assert autoeval('11') == 11 and np.isclose(autoeval('12.3'), 12.3)
    assert autoeval('a') == 'a' and autoeval(u'bc') == u'bc'
    assert autoeval('[1,2,3]') == [1,2,3]
    assert autoeval('NA') == NA and autoeval('None') is None

def test_types():
    assert isstring('abc') and isstring(u'def') and isstring(np.array(['ghi'])[0])
    assert not isstring(1) and not isstring(False)

    assert mappable({}) and mappable(defaultdict(list)) and mappable(OrderedDict())
    assert not mappable([]) and not mappable(())

    assert hashable('a') and hashable(())
    assert not hashable([]) and not hashable(slice(None))

    assert iterable([]) and iterable(xrange(5)) and iterable(iter(range(5))) and iterable('abc') and iterable(u'def')
    assert listable([]) and listable(xrange(5)) and listable(iter(range(5))) and not listable('abc') and not listable('def')
    assert isiterator(iter(range(10))) and not isiterator(range(10))

def test_checks():
    assert checkall(np.ones(10), lambda x: x == 1) and not checkall([1,0,1,1,1], lambda x: x == 1)
    assert checkany([1,0,1,1,1], lambda x: x == 1) and not checkany(np.ones(10), lambda x: x != 1)

def test_peek():
    l, c = iter(range(10)), []
    while True:
        v, l = peek(l)
        if v is None: break
        c += [v]
    assert c == range(10)
