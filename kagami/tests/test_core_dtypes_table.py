#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
test_core_dtypes_table

author(s): Albert (aki) Zhou
origin: 08-20-2018

"""


import pytest
import cPickle as cp
import numpy as np
from copy import deepcopy
from bidict import bidict
from kagami.core.dtypes import factor, _Index, Table


# index
def _create_index():
    Color = factor('Color', ['r', 'g', 'b'])
    return _Index(color = Color(arrValues = [1, 1, 0, 1, 2, 0]), index = np.arange(6), names = map(lambda x: 'n%d' % x, range(6)))

def test_index_creation():
    with pytest.raises(Exception): _Index()
    idx = _Index(size = 6)
    idx = _Index(color = [u'value'] * 6, index = np.arange(6), names = map(lambda x: 'n%d' % x, range(6)))
    idx = _Index(idx)

def test_index_built_ins():
    idx = _create_index()

    # getitem & setitem
    assert np.sum(idx['color'] == 'r') == 2
    assert np.all((idx['color'] != 'g' ) == np.array([0, 0, 1, 0, 1, 1], dtype = bool))
    assert np.all(np.where(idx['color'] == 'g')[0] == (0, 1, 3))
    assert np.all(idx[:-1]['index'] == np.arange(5))
    assert np.all(idx[-1]['names'] == np.array(['n5']))

    cidx = idx.copy()
    cidx[[1,3,5]] = idx[[0,2,4]]
    assert np.all(cidx['index'] == [0,0,2,2,4,4])

    cidx[:] = idx
    assert cidx == idx

    with pytest.raises(Exception): idx['index'] = np.arange(7)

    # add
    assert np.all((idx + idx)['index'] == np.r_[np.arange(6), np.arange(6)])
    assert idx == deepcopy(idx)
    assert idx != idx[:-1]

def test_index_properties():
    idx = _create_index()

    # size & shape
    assert idx[:-1].size == 5
    assert idx[:-1].shape == (3, 5)

def test_index_methods():
    idx1 = _create_index()
    idx2 = idx1[1:]

    # stack
    assert np.all(_Index.stack(idx1, idx2)['index'] == [0, 1, 2, 3, 4, 5, 1, 2, 3, 4, 5])

    # insert & drop
    assert np.all(idx1.insert(idx2, 2)['index'] == [0, 1, 1, 2, 3, 4, 5, 2, 3, 4, 5])
    assert np.all(idx1.drop(2)['index'] == [0, 1, 3, 4, 5])
    assert np.all(idx1.drop([1,3,5])['index'] == [0, 2, 4])

    # copy
    assert deepcopy(idx1) == idx1.copy()


# table
