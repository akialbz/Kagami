#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
test_rWrapper

author(s): Albert (aki) Zhou
added: 16-23-2023

"""


import pytest
import numpy as np
try:
    import rpy2.robjects as robj
    rpy_available = True
except ImportError:
    rpy_available = False
if rpy_available: from kagami.wrappers import RWrapper


@pytest.mark.skipif(not rpy_available, reason = 'rpy2 not installed')
def test_running():
    rw = RWrapper()
    rw.clean()

    assert len(np.array(rw.run('ls()'))) == 0

    rw.apply('data', 'iris')
    assert np.all(np.array(rw.run('dim(iris)')) == np.array([150,5]))
    assert np.all(np.array(rw.apply('dim', rw.apply('get', 'iris'))) == np.array([150,5]))
    assert np.all(np.array(rw.r.dim(rw.r['iris'])) == np.array([150,5]))

    assert np.all(np.array(rw.r.ls()) == np.array(['iris']))
    rw.clean()
    assert len(np.array(rw.apply('ls'))) == 0

@pytest.mark.skipif(not rpy_available, reason='rpy2 not installed')
def test_library():
    rw = RWrapper()
    rw.clean()

    rw.apply('install.packages', 'tinytest')
    assert rw.installed('tinytest')
    rw.library('tinytest')
    assert np.array(rw.r.expect_match('hello world', 'world'))

    rw.clean()

@pytest.mark.skipif(not rpy_available, reason='rpy2 not installed')
def test_variable():
    rw = RWrapper()
    rw.clean()

    vals = np.arange(3)
    nams = np.array(['a','b','c'])
    vct = rw.asVector(vals, nams)
    assert np.all(np.array(rw.r.length(vct)) == np.array([3]))

    rw.assign(vct, 'vct')
    assert np.all(np.array(rw.r['vct']) == vals)
    assert np.all(np.array(rw.r.names(rw.r['vct'])) == nams)

    vals = np.arange(12).reshape((2,6))
    rnams = np.array(['aa','bb','cc','dd'])
    cnams = np.array(['v1','v2','v3'])
    mtx = rw.asMatrix(vals, nrow = 4, rownames = rnams, colnames = cnams)
    assert np.all(np.array(rw.r.dim(mtx)) == np.array([4,3]))

    rw.assign(mtx, 'mtx')
    assert np.all(np.array(rw.r['mtx']) == vals.reshape((4,3)))
    assert np.all(np.array(rw.r['row.names'](rw.r['mtx'])) == rnams)
    assert np.all(np.array(rw.r['colnames' ](rw.r['mtx'])) == cnams)

    rw.clean()
