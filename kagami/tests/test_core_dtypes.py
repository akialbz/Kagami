#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
test_core_dtypes

author(s): Albert (aki) Zhou
origin: 08-15-2018

"""


import cPickle as cp
import numpy as np
from bidict import bidict
from kagami.core.dtypes import factor


# factor
def test_factor():
    cdct = bidict(r = 1, g = 2, b = 3)
    Color = factor('Color', cdct)

    arr1 = np.array([2, 3, 2, 1, 3, 1, 2])
    arr2 = np.array([1, 1, 3, 1, 3])

    col1 = Color(arrValues = arr1)
    col2 = Color(array = [cdct.inv[v] for v in arr2])

    # build-ins
    assert np.all(col1[1:4].arrValues == arr1[1:4])
    col1[-1:] = 'r'
    assert np.all(col1[-2:] == np.array(['r', 'r']))
    col1[-1:] = 'g'
    assert np.all(np.array([cdct[v] for v in col2]) == arr2)
    assert np.all((col1 == 'g') == (arr1 == 2))
    assert 'r' in col2 and 'g' not in col2
    assert np.all((col1+col2).arrValues == np.hstack((arr1, arr2)))
    assert len(col1+col2) == arr1.shape[0] + arr2.shape[0]

    # numpy interface
    assert np.all(np.insert(col1, 2, 'b').array == np.array([cdct.inv[v] for v in np.insert(arr1, 2, 3)]))
    assert np.all(np.delete(col1, 3).arrValues == np.delete(arr1, 3))

    # pickle
    assert np.all(cp.loads(cp.dumps(col1)).arrValues == arr1)

    # properties
    assert np.all(col1.array == np.array([cdct.inv[v] for v in arr1]))
    assert np.all(col2.arrValues == arr2)
    assert col1.size == len(arr1) and col2.size == len(arr2)

    # class methods
    assert set(Color.levels()) == {'r', 'g', 'b'}
    assert set(Color.values()) == {1, 2, 3}
    assert np.all(Color.encode([cdct.inv[v] for v in arr1]) == arr1)
    assert np.all(Color.decode(arr2) == np.array([cdct.inv[v] for v in arr2]))
    assert np.all(Color.stack(col1, col2).arrValues == np.hstack((arr1, arr2)))

    # piublic methods
    assert np.all(col1.insert(col2, 3) == np.insert(col1, 3, col2))
    assert np.all(col1.insert(col2).arrValues == np.hstack((arr1, arr2)))
    assert np.all(col1.drop(2).arrValues == np.delete(col1, 2).arrValues)
    ccol1 = col1.copy()
    assert ccol1 is not col1 and np.all(ccol1 == col1)


# table

