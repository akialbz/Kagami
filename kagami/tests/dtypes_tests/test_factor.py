#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
test_core_dtypes_factor

author(s): Albert (aki) Zhou
origin: 08-15-2018

"""


import pytest
import cPickle as cp
import numpy as np
from copy import deepcopy
from bidict import bidict
from kagami.dtypes import factor, asFactor


# factor
def _create_factor():
    cdct = bidict(r = 1, g = 2, b = 3)
    Color = factor('Color', cdct)

    arr1 = np.array([2, 3, 2, 1, 3, 1, 2])
    arr2 = np.array([1, 1, 3, 1, 3])

    col1 = Color(array = arr1)
    col2 = Color(labels = [cdct.inv[v] for v in arr2])
    return cdct, (arr1, arr2), (col1, col2)

def test_factor_creation():
    cdct = dict(r = 1, g = 2, b = 3)
    Color = factor('Color', cdct.keys())
    Color = factor('Color', cdct)

    assert Color.r == 1 and Color.g == 2 and Color.b == 3

    Color()
    Color(['r', 'r', 'g', 'b', 'g'])
    Color(Color(['r', 'r', 'b', 'g']))
    Color(array = [2, 1, 3, 2])

    with pytest.raises(TypeError): factor('Color', None)
    with pytest.raises(KeyError): Color(['r', 'black', 'g', 'b'])
    with pytest.raises(ValueError): Color(array = [0, 2, 1, 3, 4])

    assert set(asFactor(['a', 'a', 'b', 'a', 'c', 'b']).levels()) == {'a', 'b', 'c'}

def test_factor_built_ints():
    cdct, (arr1, arr2), (col1, col2) = _create_factor()

    # item oprtations
    assert np.all(col1[1:4].array == arr1[1:4])
    assert np.all(col1[-1].array == arr1[[-1]])
    assert np.all(col1[[0,2]].array == arr1[[0,2]])
    assert np.all(col2[np.array([0,1,1,0,1], dtype = bool)] == [cdct.inv[v] for v in arr2[[1,2,-1]]])
    assert np.all(col2.array == arr2)
    assert np.all(col1[3:5].array == col2[3:5].array)

    ccol = deepcopy(col1)
    ccol[-3:] = 'r'
    assert np.all(ccol[-3:].array == 1)
    ccol[:-1] = 'g'
    assert np.all(ccol.array == [2, 2, 2, 2, 2, 2, 1])
    ccol[:] = 'b'
    assert np.all(ccol.array == 3)

    ccol = deepcopy(col1)
    del ccol[-1]
    assert np.all(ccol.array == arr1[:-1])
    del ccol[[0,2]]
    assert np.all(ccol.array == [3, 1, 3, 1])

    # sequence oprtations
    assert np.all(arr2 == [cdct[v] for v in col2])
    assert 'r' in col1 and 'r' in col2
    assert 'g' in col1 and 'g' not in col2
    assert 'b' not in col2[:2]
    assert len(col1) == arr1.shape[0]
    assert len(col2[-1]) == 1

    # comparison oprtations
    assert np.all((col1 == 'g') == (arr1 == 2))
    assert np.all((col2 != 'g') == np.ones_like(col2, dtype = bool))
    assert np.all(col1 == [cdct.inv[v] for v in arr1])
    assert np.all(col1[3:5] == col2[3:5])

    # arithmetic oprtations
    assert np.all(col1[[0,2]] + col1[[1,3]] == col1[[0,2,1,3]])
    assert np.all((col1 + ['r', 'g']).array == np.hstack((arr1, [1, 2])))
    assert np.all((col1 + col2).labels == (col1 + col2))
    assert np.all((col1 + col2).array == np.hstack((arr1, arr2)))

    ccol = deepcopy(col1)
    ccol += col2
    assert np.all(ccol == col1 + col2)
    ccol += np.array(['b', 'b'])
    assert np.all(ccol.array == np.hstack((arr1, arr2, [3, 3])))

    with pytest.raises(KeyError): ccol += ['yellow']

    # representation oprtations
    print col1
    print str(col1)
    print repr(col1)

    # numpy array interface
    assert np.all(np.insert(col1, 1, 'b').array == np.insert(arr1, 1, 3))
    assert np.all(np.insert(col1, [2,3], ['r','b']).array == np.insert(arr1, [2,3], [1,3]))
    assert np.all(np.delete(col1, -1).array == np.delete(arr1, -1))
    assert np.all(np.delete(col1, [0,2]).array == np.delete(arr1, [0,2]))
    assert len(np.delete(col2,[0,1,2,3,4])) == 0

    with pytest.raises(KeyError): np.insert(col1, -1, 'yellow')

    # pickle
    assert np.all(col1 == cp.loads(cp.dumps(col1)))

def test_factor_properties():
    cdct, (arr1, arr2), (col1, col2) = _create_factor()

    # lavel properties
    assert col1.r == col2.r == 1 and col1.g == col2.g == 2 and col1.b == col2.b == 3

    # labels & array
    assert np.all(col1.labels == np.array([cdct.inv[v] for v in arr1]))
    assert np.all(col2.labels == np.array([cdct.inv[v] for v in arr2]))
    assert np.all(col1.array == arr1)
    assert np.all(col2.array == arr2)

    # size
    assert col1.size == len(arr1) == len(col1)
    assert col2.size == len(arr2) == len(col2)
    assert col1.shape == arr1.shape
    assert col1.ndim == col2.ndim == 1

def test_factor_methods():
    cdct, (arr1, arr2), (col1, col2) = _create_factor()

    # class methods
    cls = col1.__class__
    assert col2.__class__ is cls
    assert isinstance(col2, cls)

    assert set(cls.levels()) == {'r', 'g', 'b'}
    assert set(cls.values()) == {1, 2, 3}
    assert set(cls.items()) == set(cdct.items())

    assert np.all(cls.encode([cdct.inv[v] for v in arr1]) == arr1)
    assert np.all(cls.decode(arr2) == np.array([cdct.inv[v] for v in arr2]))
    assert np.all(cls.encode(col1) == arr1)
    assert np.all(cls.decode(col2) == col2.labels)
    assert np.all(cls.encode('r') == [1])
    assert np.all(cls.decode(2) == ['g'])

    # piublic methods
    # manipulations
    assert np.all(col1.append(['r', 'g']).array == np.hstack((arr1, [1,2])))
    assert np.all(col1.append('b').array == np.hstack((arr1, 3)))
    with pytest.raises(KeyError): col1.append('yellow')

    assert np.all(col1.insert(col2, 3) == np.insert(col1, 3, col2))
    assert np.all(col1.insert(col2).array == np.hstack((arr1, arr2)))
    assert np.all(col1.insert('b', 0).array == np.insert(arr1, 0, 3))
    with pytest.raises(KeyError): col1.insert('yellow', 2)

    assert np.all(col1.drop(2) == np.delete(col1, 2))
    assert np.all(col1.drop(-1).array == arr1[:-1])

    # copy
    ccol1 = col1.copy()
    assert ccol1 is not col1
    assert np.all(ccol1 == col1)

