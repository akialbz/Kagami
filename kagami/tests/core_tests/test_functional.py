#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
test_functional

author(s): Albert (aki) Zhou
origin: 11-20-2018

"""


import numpy as np
from kagami.core import *


def test_partial():
    def _add(a, b, c = 3): return a, b, c
    assert partial(_add, 1)(2) == (1, 2, 3)
    assert partial(_add, 2, 3)(4) == (2, 3, 4)
    assert partial(_add, 3, c = 5)(4) == (3, 4, 5)
    assert partial(_add, b = 5, c = 6)(4) == (4, 5, 6)

def test_compose():
    def _ext(a,v): a += [v]; return a
    assert compose(partial(_ext, v = 1), partial(_ext, v = 2))([0]) == [0, 1, 2]

def _pow(*args): return np.power(args, 2)
def _mp_pow(args): return _pow(*args)

def test_maps():
    vals = np.random.uniform(0, 10, size = (3, 5))
    assert np.allclose(smap(vals, unpack(_pow)), np.power(vals, 2))
    assert np.allclose(tmap(vals, _mp_pow), np.power(vals, 2))
    assert np.allclose(pmap(vals, _mp_pow), np.power(vals, 2))
    assert np.allclose(cmap(vals, _mp_pow), np.power(vals, 2))
    assert np.allclose(call(vals, (_mp_pow, _mp_pow), nthreads = 6, collect = lambda x: np.array(x) - 1), np.power(vals, 4) - 1)
    assert np.allclose(call(vals, (_mp_pow, _mp_pow), nprocs = 6, collect = lambda x: np.array(x) - 1), np.power(vals, 4) - 1)

def test_pickdrop():
    vals = np.random.uniform(-10, 10, size = 10)
    assert np.allclose(pick(vals, lambda x: x > 0), vals[vals > 0])
    assert np.allclose(pick(vals, vals[1]), vals[np.isclose(vals, vals[1])])
    assert np.allclose(pickmap(vals, lambda x: x < 0, lambda x: x * -1), np.abs(vals))

    assert np.allclose(drop(vals, lambda x: x < 0), vals[vals > 0])
    assert np.allclose(drop(vals, vals[1]), vals[~np.isclose(vals, vals[1])])

def test_folds():
    vals = np.random.uniform(-10, 10, size = 10)
    assert np.isclose(fold(vals, lambda x,y: x+y), np.sum(vals))
    assert np.isclose(collapse(vals), np.sum(vals))

    valv = [[v] for v in vals]
    assert np.allclose(fold(valv, lambda x,y: x+y), vals)
    assert np.allclose(collapse(valv), vals)
