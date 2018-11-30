#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
test_core.py

author(s): Albert (aki) Zhou
origin: 11-14-2018

"""


import cPickle as cp
from kagami.core import *


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

    del meta.c
    assert set(meta.items()) == {('a', 4), ('b', 2)}

    assert cp.loads(cp.dumps(meta)) == meta

