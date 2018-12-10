#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
test_dtypes_structArray

author(s): Albert (aki) Zhou
origin: 09-25-2018

"""


import os, pytest
import cPickle as cp
import numpy as np
from copy import deepcopy
from kagami.core import *
from kagami.dtypes import factor, NamedIndex, StructuredArray


def _create_structArray():
    colors = factor('Colors', ('r', 'g', 'b'))
    arr = StructuredArray([
        ('ser1', np.array([1, 3, 5, 7, 9])),
        ('ser2', np.array([0.2, 0.4, 0.6, 0.8, 1.0])),
        ('ser3', np.array(['v1', 'v2', 'v3', 'v4', 'v5'])),
        ('ser4', np.array([0, 1, 1, 0, 1], dtype = bool)),
        ('ser5', colors(array = [0, 1, 1, 2, 1])),
        ('ser6', NamedIndex(['n1', 'n2', 'n3', 'n4', 'n5'])),
    ])
    return arr

def test_structArray_creation():
    StructuredArray()
    StructuredArray([('a', [1,2,3]), ('b', ['j', 'k', 'l'])])
    StructuredArray(a = [2., 4., 6.], b = [True, True, False])
    with pytest.raises(ValueError): StructuredArray(a = [1,2,3], b = ['i','j'])
    with pytest.raises(ValueError): StructuredArray(a = 'abcde')

def test_structArray_built_ins():
    arr = _create_structArray()

    # item oprtations
    assert np.all(arr['ser1'] == np.array([1,3,5,7,9]))
    assert np.all(arr['ser5'].labels == ['r', 'g', 'g', 'b', 'g'])
    assert np.all(arr['ser6'][:3] == ['n1', 'n2', 'n3'])
    assert np.all(arr['ser2',1:-1] == [[0.4, 0.6, 0.8]])
    assert np.all(arr[-3,1:] == [True, True, False, True])
    assert np.all(arr[2:4,-1] == [['v5'], [True]])
    assert np.all(arr[[False, False, False, True, True, False],-1] == [[True], ['g']])
    assert np.all(arr[:2,[False, True, False, False, False]] == [[3], [0.4]])
    assert np.all(arr[0,[True, True, False, False, True]] == [1, 3, 9])

    carr = deepcopy(arr)
    carr[:,2:] = arr[:,2:]
    assert carr == arr
    carr['ser2'] = [1,3,5,7,9]
    assert np.all(carr['ser2'] == carr['ser1'])
    carr[:2,3:] = 0
    assert np.all(carr[['ser1','ser2'],3:] == 0)
    carr[[1,2],[3,4]] = 1
    assert np.all(carr[[1,2],[3,4]] == [[1., 1.], ['1', '1']])
    carr[-2:,-2:] = [['r', 'b'], ['n6', 'n7']]
    assert np.all(carr['ser5'].array == [0, 1, 1, 0, 2])
    assert np.all(carr['ser6'] == ['n1', 'n2', 'n3', 'n6', 'n7'])
    carr['ser5'] = np.array(carr['ser5'])
    assert carr['ser5'].dtype.kind == 'S' and np.all(carr['ser5'] == ['r', 'g', 'g', 'r', 'b'])
    carr['ser5'][:-1] = na
    assert np.all(carr['ser5'] == ['', '', '', '', 'b'])
    carr['ser3',:] = np.arange(5)
    assert np.all(carr['ser3'] == ['0', '1', '2', '3', '4'])
    carr['ser3'] = np.arange(5)
    assert np.all(carr['ser3'] == [0, 1, 2, 3, 4])
    carr['ser3'][1:3] = na
    assert np.all(isna(carr['ser3']) == [False, True, True, False, False])

    carr = deepcopy(arr)
    del carr['ser1']
    assert np.all(carr.names == ['ser2', 'ser3', 'ser4', 'ser5', 'ser6'])
    del carr[[0,1]]
    assert np.all(carr.names == ['ser4', 'ser5', 'ser6'])
    del carr[:,-2:]
    assert np.all(carr[:] == [[False, True, True], ['r', 'g', 'g'], ['n1', 'n2', 'n3']])
    del carr[:]
    assert len(carr) == 0

    # sequence oprtations
    assert np.all(np.array([n for n in arr]) == ['ser1', 'ser2', 'ser3', 'ser4', 'ser5', 'ser6'])
    assert 'ser1' in arr
    assert 'ser10' not in arr
    assert len(arr) == 6

    # comparison oprtations
    assert np.all(arr == arr.values)
    assert np.all((arr == 1) == (arr.values == 1))
    assert arr == deepcopy(arr)

    # arithmetic oprtations
    assert arr[:,:2] + arr[:,2:] == arr
    carr = deepcopy(arr)[:,:-1]
    carr += arr[:,-1]
    assert carr == arr
    carr = deepcopy(arr)[:,:2]
    carr['ser7'] = ['a', 'b']
    with pytest.raises(KeyError): carr += arr[:,2:]

    # representation oprtations
    print arr
    print str(arr)
    print repr(arr)

    # numpy array interface
    assert np.all(np.array(arr) == arr.values)

    # pickle
    assert arr == cp.loads(cp.dumps(arr))

def test_structArray_properties():
    arr = _create_structArray()

    # names
    assert np.all(arr.names == map(lambda x: 'ser%d' % (x+1), range(6)))

    # series and values
    assert arr.values.shape == (6,5)
    assert len(arr.series) == 6 and set(map(len, arr.series)) == {5}
    assert arr.items == zip(arr.names, arr.series)

    # sizes
    assert arr.size == 6
    assert arr.length == 5
    assert arr.shape == (6,5)
    assert arr.ndim == 2

def test_structArray_methods():
    arr = _create_structArray()

    # manipulations
    assert arr[:,:2] + arr[:,2:] == arr
    assert arr[:,:2].append(arr[:,2:]) == arr

    assert arr[:,[0,1,4]].insert(arr[:,[2,3]], 2) == arr
    assert arr[:,:2].insert(arr[:,2:]) == arr

    assert np.all(arr.drop(-1)[0] == [1,3,5,7])
    assert np.all(arr.drop(slice(1,-1))[-1] == ['n1', 'n5'])

    # copy
    assert arr == arr.copy()
    assert arr is not arr.copy()

    # portals
    fname = 'test_structArray'

    arr.savecsv(fname + '.csv')
    larr = StructuredArray.loadcsv(fname + '.csv')
    print larr
    assert larr == arr
    if os.path.isfile(fname + '.csv'): os.remove(fname + '.csv')

    arr.savehdf(fname + '.hdf', compression = 9)
    larr = StructuredArray.loadhdf(fname + '.hdf')
    print larr
    assert larr == arr
    if os.path.isfile(fname + '.hdf'): os.remove(fname + '.hdf')

