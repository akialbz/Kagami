#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
test_etc.py

author(s): Albert (aki) Zhou
origin: 11-14-2018

"""


import numpy as np
from collections import defaultdict, OrderedDict
from kagami.core import *


def test_autoeval():
    assert autoeval('11') == 11 and np.isclose(autoeval('12.3'), 12.3)
    assert autoeval('a') == 'a' and autoeval(u'bc') == u'bc'
    assert autoeval('[1,2,3]') == [1,2,3]
    assert autoeval('na') == autoeval('n/a') == autoeval('NA') == autoeval('N/A') == na
    assert autoeval('None') is None

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
    def _test(_wrap):
        l, c = _wrap(range(10)), []
        while True:
            v, l = peek(l)
            if v is None: break
            c += [v]
        assert c == range(10)
    _test(list)
    _test(iter)
    _test(np.array)

