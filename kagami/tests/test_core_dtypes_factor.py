#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
test_core_dtypes_factor

author(s): Albert (aki) Zhou
origin: 08-15-2018

"""


import cPickle as cp
import numpy as np
from bidict import bidict
from kagami.core.dtypes import factor


# factor
def _create_factor():
    cdct = bidict(r = 1, g = 2, b = 3)
    Color = factor('Color', cdct)

    arr1 = np.array([2, 3, 2, 1, 3, 1, 2])
    arr2 = np.array([1, 1, 3, 1, 3])

    col1 = Color(arrValues = arr1)
    col2 = Color(array = [cdct.inv[v] for v in arr2])
    return cdct, (arr1, arr2), (col1, col2)

def test_factor_built_ints():
    cdct, (arr1, arr2), (col1, col2) = _create_factor()

    # getitem & setitem
    assert np.all(col1[1:4].arrValues == arr1[1:4])
    assert np.all(col2.arrValues == arr2)

    col1[-1:] = 'r'
    arr1[-1] = 1
    assert np.all(col1[-2:] == np.array(['r', 'r']))
    assert np.all(col1.arrValues == arr1)

    # iter
    assert np.all(np.array([cdct[v] for v in col2]) == arr2)

    # eq & ne
    assert np.all((col1 == 'g') == (arr1 == 2))
    assert np.all((col2 != 'g') == np.ones_like(col2, dtype = bool))
    assert np.all(col1 == [cdct.inv[v] for v in arr1])
    assert np.all(col1[:-1] == col1[0:arr1.shape[0]-1])

    # contains
    assert 'r' in col1
    assert 'g' not in col2

    # add & len
    assert np.all((col1+col2).arrValues == np.hstack((arr1, arr2)))
    assert len(col1+col2) == arr1.shape[0] + arr2.shape[0]

    # numpy interface
    assert np.all(np.insert(col1, 2, 'b').array == np.array([cdct.inv[v] for v in np.insert(arr1, 2, 3)]))
    assert np.all(np.delete(col1, 3).arrValues == np.delete(arr1, 3))

    # pickle
    assert np.all(cp.loads(cp.dumps(col1)) == col1)

def test_factor_properties():
    cdct, (arr1, arr2), (col1, col2) = _create_factor()

    # array
    assert np.all(col1.array == np.array([cdct.inv[v] for v in arr1]))

    # arrValues
    assert np.all(col2.arrValues == arr2)

    # size
    assert col1.size == len(arr1) == len(col1)
    assert col2.size == len(arr2) == len(col2)

def test_factor_methods():
    cdct, (arr1, arr2), (col1, col2) = _create_factor()

    # class methods
    cls = col1.__class__
    assert col2.__class__ is cls
    # levels & values & items
    assert set(cls.levels()) == {'r', 'g', 'b'}
    assert set(cls.values()) == {1, 2, 3}
    assert set(cls.items()) == set(cdct.items())

    # encode & decode
    assert np.all(cls.encode([cdct.inv[v] for v in arr1]) == arr1)
    assert np.all(cls.decode(arr2) == np.array([cdct.inv[v] for v in arr2]))

    # stack
    assert np.all(cls.stack(col1, col2) == [cdct.inv[v] for v in np.hstack((arr1, arr2))])

    # piublic methods
    # insert
    assert np.all(col1.insert(col2, 3) == np.insert(col1, 3, col2))
    assert np.all(col1.insert(col2).arrValues == np.hstack((arr1, arr2)))

    # drop
    assert np.all(col1.drop(2).arrValues == np.delete(col1, 2).arrValues)

    # put
    col2.put(2, 'r')
    assert np.all(col2.arrValues == [1, 1, 1, 1, 3])
    col2.put([0,1], 'b')
    assert np.all(col2.arrValues == [3, 3, 1, 1, 3])
    col2.put([2,3], ['g','g'])
    assert np.all(col2.arrValues == [3, 3, 2, 2, 3])

    # copy
    ccol1 = col1.copy()
    assert ccol1 is not col1
    assert np.all(ccol1 == col1)

