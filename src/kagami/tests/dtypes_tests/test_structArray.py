#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
test_dtypes_structArray

author(s): Albert (aki) Zhou
added: 09-25-2018

"""


import pytest
import pickle as pkl
import numpy as np
from pathlib import Path
from copy import deepcopy
from kagami.comm import smap
from kagami.dtypes import NamedIndex, StructuredArray


def _create_structArray():
    arr = StructuredArray([
        ('ser1', np.array([1, 3, 5, 7, 9])),
        ('ser2', np.array([0.2, 0.4, 0.6, 0.8, 1.0])),
        ('ser3', iter(np.array(['v1', 'v2', 'v3', 'v4', 'v5']))),
        ('ser4', np.array([0, 1, 1, 0, 1], dtype = bool)),
        ('ser5', ['r', 'g', 'g', 'b', 'g']),
        ('ser6', NamedIndex(['n1', 'n2', 'n3', 'n4', 'n5'])),
    ])
    return arr

def test_structArray_creation():
    StructuredArray()
    StructuredArray([('a', [1,2,3]), ('b', ['j', 'k', 'l'])])
    StructuredArray({'a': (1,2,3), 'b': iter([4,5,6])})
    StructuredArray(StructuredArray(a = [1,2,3], b = [4,5,6]))
    StructuredArray(a = [2., 4., 6.], b = [True, True, False])
    with pytest.raises(ValueError): StructuredArray(a = [1,2,3], b = ['i','j'])
    with pytest.raises(ValueError): StructuredArray(a = 'abcde')

def test_structArray_built_ins_item_operations():
    arr = _create_structArray()

    assert np.all(arr['ser1'] == np.array([1,3,5,7,9]))
    assert np.all(arr['ser5'] == ['r', 'g', 'g', 'b', 'g'])
    assert np.all(arr['ser6'][:3] == ['n1', 'n2', 'n3'])
    assert np.all(arr['ser2',1:-1] == [[0.4, 0.6, 0.8]])
    assert np.all(arr[-3,1:] == [[True, True, False, True]])

    assert np.all(arr.ser1 == np.array([1,3,5,7,9]))
    assert np.all(arr.ser5 == ['r', 'g', 'g', 'b', 'g'])
    assert np.all(arr.ser6[:3] == ['n1', 'n2', 'n3'])

    assert np.all(arr[2:4,-1] == [['v5'], [True]])
    assert np.all(arr[[False, False, False, True, True, False],-1] == [[True], ['g']])
    assert np.all(arr[:2,[False, True, False, False, False]] == [[3], [0.4]])
    assert np.all(arr[0,[True, True, False, False, True]] == [1, 3, 9])

    carr = deepcopy(arr)
    carr[:,2:] = arr[:,2:]
    assert carr == arr
    carr.ser2[:] = [1,3,5,7,9]
    assert np.all(carr['ser2'] == carr['ser1'])
    carr[:2,3:] = 0
    assert np.all(carr[['ser1','ser2'],3:] == 0)
    carr[[1,2],[3,4]] = 1
    assert np.all(carr[[1,2],[3,4]] == [[1., 1.], ['1', '1']])
    carr[-2:,-2:] = [['r', 'b'], ['n6', 'n7']]
    assert np.all(carr.ser5 == ['r', 'g', 'g', 'r', 'b'])
    assert np.all(carr['ser6'] == ['n1', 'n2', 'n3', 'n6', 'n7'])
    carr.ser5[:] = np.array(carr['ser5'])
    assert carr['ser5'].dtype.kind == 'U' and np.all(carr['ser5'] == ['r', 'g', 'g', 'r', 'b'])
    carr['ser5'][:-1] = None
    assert np.all(carr['ser5'] == [['N', 'N', 'N', 'N', 'b']])
    carr['ser3',:] = np.arange(5)
    assert np.all(carr.ser3 == ['0', '1', '2', '3', '4'])
    carr['ser3'] = np.arange(5)
    assert np.all(carr.ser3 == [0, 1, 2, 3, 4])
    carr.ser3[1:3] = -1
    assert np.all((carr['ser3'] == -1) == [False, True, True, False, False])

    carr = deepcopy(arr)
    del carr['ser1']
    assert np.all(carr.names == ['ser2', 'ser3', 'ser4', 'ser5', 'ser6'])
    del carr[[0,1]]
    assert np.all(carr.names == ['ser4', 'ser5', 'ser6'])
    del carr[:,-2:]
    assert np.all(carr[:] == [[False, True, True], ['r', 'g', 'g'], ['n1', 'n2', 'n3']])
    del carr[:]
    assert len(carr) == 0
    carr['ser7'] = ['1', '2', '3']
    assert np.all(carr.ser7.astype(int) == [1,2,3])

def test_structArray_built_ins_seq_operations():
    arr = _create_structArray()
    assert np.all(np.array([n for n in arr]) == ['ser1', 'ser2', 'ser3', 'ser4', 'ser5', 'ser6'])
    assert 'ser1' in arr
    assert 'ser10' not in arr
    assert len(arr) == 6

def test_structArray_built_ins_comparisons():
    arr = _create_structArray()
    assert np.all(arr == arr.arrays)
    assert np.all((arr == 1) == [[v == 1 for v in ar] for ar in arr.arrays])
    assert arr == deepcopy(arr)
    assert arr != arr[:,1:]

def test_structArray_built_ins_arithmetic_oprtations():
    arr = _create_structArray()

    assert arr[:,:2] + arr[:,2:] == arr
    carr = deepcopy(arr)[:,:-1]
    carr += arr[:,-1]
    assert carr == arr
    carr = deepcopy(arr)[:,:2]
    carr['ser7'] = ['a', 'b']
    with pytest.raises(KeyError): carr += arr[:,2:]

def test_structArray_built_ins_representations():
    arr = _create_structArray()
    print(arr)
    print(str(arr))
    print(repr(arr))

def test_structArray_built_ins_numpy_interfaces():
    arr = _create_structArray()
    assert np.all(np.array(arr, dtype = object) == np.array(arr.arrays, dtype = object))
    assert np.all(np.array(arr).dtype.names == arr.names)

def test_structArray_built_ins_pkls():
    arr = _create_structArray()
    assert arr == pkl.loads(pkl.dumps(arr))

def test_structArray_properties_names():
    arr = _create_structArray()
    assert np.all(arr.names == list(map(lambda x: 'ser%d' % (x+1), range(6))))

def test_structArray_properties_items():
    arr = _create_structArray()
    assert len(arr.arrays) == 6 and set(map(len, arr.arrays)) == {5}
    assert np.all(np.array(arr.names) == list(zip(*arr.fields))[0]) and \
           np.all(np.array(arr.arrays, dtype = object) == np.array(list(zip(*arr.fields))[1], dtype = object))

def test_structArray_properties_sizes():
    arr = _create_structArray()
    assert arr.size == 6
    assert arr.length == 5
    assert arr.shape == (6,5)
    assert arr.ndim == 2

def test_structArray_methods_manipulations():
    arr = _create_structArray()

    carr = deepcopy(arr)
    assert np.all(carr.take('ser1') == [1,3,5,7,9])
    assert np.all(carr.take(['ser1', 'ser4']) == [[1,3,5,7,9], [0,1,1,0,1]])
    assert np.all(carr.take((slice(None,2), [False, True, True, False, True]), axis = None) == [[3,5,9], [0.4,0.6,1.]])
    assert np.all(carr.take((slice(None), -1), axis = None) == [[9], [1.], ['v5'], [True], ['g'], ['n5']])
    assert np.all(carr.take(-1, axis = 1) == [[9], [1.], ['v5'], [True], ['g'], ['n5']])

    assert np.all(carr.put('ser2', [2,4,6,8,0], inline = False).ser2 == [2.,4.,6.,8.,0.])
    assert np.all(carr.put(-1, 0, axis = 1, inline = False)[:,-1] == [[0], [0.], ['0'], [False], ['0'], ['0']])
    assert np.all(carr.put((['ser1', 'ser2'], slice(2,4)), 1, axis = None, inline = False)[:2,2:4] == 1)
    assert carr == arr
    carr.put(slice(None), 1, inline = True)
    assert np.all(np.logical_or(carr == 1, carr == '1')) and carr != arr

    assert arr[:,:2] + arr[:,2:] == arr
    assert arr[:,:2].append(arr[:,2:]) == arr
    assert np.all(arr.append(1, inline = False)[:,-1] == [[1], [1.], ['1'], [True], ['1'], ['1']])

    assert arr[:,[0,1,4]].insert(2, arr[:,[2,3]]) == arr
    assert arr[:,:2].insert(None, arr[:,2:]) == arr
    assert np.all(arr.insert(-1, 1, inline = False)[:,-2] == [[1], [1.], ['1'], [True], ['1'], ['1']])

    assert np.all(arr.delete(-1, axis = 1, inline = False)[0] == [1,3,5,7])
    assert np.all(arr.delete('ser1', inline = False).names == ['ser2', 'ser3', 'ser4', 'ser5', 'ser6'])
    assert np.all(arr.delete((None, [3,4]), axis = None, inline = False)[0] == [1,3,5])
    assert np.all(arr.delete(slice(1,-1), axis = 1, inline = False)[-1] == ['n1', 'n5'])

def test_structArray_methods_copy():
    arr = _create_structArray()
    assert arr == arr.copy()
    assert arr is not arr.copy()

def test_structArray_portals():
    arr = _create_structArray()

    assert np.all(arr.tosarray(withdtype = False) == np.array([[k]+smap(vs,str) for k,vs in arr.fields]))

    fname = Path('test_structArray.csv')
    arr.savecsv(fname)
    larr = StructuredArray.loadcsv(fname)
    print(larr)
    assert larr == arr
    if fname.is_file(): fname.unlink()

    fname = Path('test_structArray.hdf')
    arr.savehdf(fname, compression = 9)
    larr = StructuredArray.loadhdf(fname)
    print(larr)
    assert larr == arr
    if fname.is_file(): fname.unlink()

