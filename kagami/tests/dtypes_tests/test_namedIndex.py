#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
test_dtypes_namedIndex

author(s): Albert (aki) Zhou
added: 08-23-2018

"""


import os, pytest
import pickle as pkl
import numpy as np
from string import ascii_lowercase
from copy import deepcopy
from kagami.dtypes import NamedIndex


def _create_namedIndex():
    vals = ['a', 'bbb', 'cc', 'dddd']
    return NamedIndex(vals), np.array(vals)

def test_namedIndex_creation():
    NamedIndex()
    NamedIndex(['aa'])
    NamedIndex(['a', 'b', 'cc'])

    with pytest.raises(TypeError): NamedIndex(['a', ['b', 'c']])
    with pytest.raises(KeyError): NamedIndex(['a', 'a', 'b'])

    idx = NamedIndex(NamedIndex.uniquenames(['a', 'a', 'b']))
    assert np.all(idx == ['a', 'a.1', 'b'])
    assert np.all(idx == NamedIndex(idx))

    print('\n', repr(NamedIndex(['%s%d' % (c,n) for c in ascii_lowercase for n in range(5)])))

def test_namedIndex_built_ins_item_oprtations():
    idx, vals = _create_namedIndex()

    assert np.all(idx[:3] == vals[:3])
    assert np.all(idx[-1] == NamedIndex(['dddd']))
    assert np.all(idx[[0,2]] == NamedIndex(vals[[0,2]]))
    assert np.all(idx == vals)

    cidx = deepcopy(idx)
    cidx[:2] = ['aa', 'bb']
    assert np.all(cidx == ['aa', 'bb', 'cc', 'dddd'])
    cidx[-1] = 'dd'
    assert np.all(cidx == NamedIndex(['aa', 'bb', 'cc', 'dd']))
    cidx[:] = ['a', 'bbb', 'cc', 'dddd']
    assert np.all(cidx == vals)
    cidx[:2] = cidx[:2]
    assert np.all(cidx == vals)

    cidx = deepcopy(idx)
    cidx['a'] = 'aa'
    assert np.all(cidx == ['aa', 'bbb', 'cc', 'dddd'])
    cidx[['bbb', 'dddd']] = iter(['bb', 'dd'])
    assert np.all(cidx == ['aa', 'bb', 'cc', 'dd'])
    cidx[[False, True, True, False]] = ['ee', 'ff']
    cidx[[1,2]] = ['ee', 'ff']
    with pytest.raises(IndexError): cidx[1,2] = ['ee', 'ff']

    with pytest.raises(KeyError): cidx[1] = 'aa'
    with pytest.raises(TypeError): cidx[:] = 1

    cidx = deepcopy(idx)
    del cidx[[1,2]]
    assert np.all(cidx == ['a', 'dddd'])
    del cidx[-1]
    assert np.all(cidx == NamedIndex(['a']))
    del cidx['a']
    assert np.all(cidx == [])

def test_namedIndex_built_ins_attr_access():
    idx, vals = _create_namedIndex()
    assert idx.a == 0 and idx.bbb == 1 and idx.cc == 2 and idx.dddd == 3

def test_namedIndex_built_ins_seq_operations():
    idx, vals = _create_namedIndex()
    assert np.all(vals == [n for n in idx])
    assert 'a' in idx
    assert 'aa' not in idx
    assert 'a' not in idx[1:]
    assert len(idx) == vals.shape[0]
    assert len(idx[-1]) == len(vals[-1])

def test_namedIndex_built_ins_comparisons():
    idx, vals = _create_namedIndex()
    assert np.all(idx == vals)
    assert np.all((idx == 'a') == [True, False, False, False])
    assert np.sum(idx == np.array('abc')) == 0
    assert np.sum(idx == NamedIndex(['bbb'])) == 1

def test_namedIndex_built_ins_arithmetic_oprtations():
    idx, vals = _create_namedIndex()

    assert np.all(idx + ['ee', 'fff'] == np.hstack((vals, ['ee', 'fff'])))
    assert np.all(idx[[0,2]] + idx[[1,3]] == idx[[0,2,1,3]])
    assert np.all(idx == vals)

    cidx = deepcopy(idx)
    cidx += 'eee'
    assert np.all(cidx == idx + ['eee'])
    cidx += np.array(['ff', 'gg'])
    assert np.all(cidx == idx + ['eee', 'ff', 'gg'])

    with pytest.raises(KeyError): cidx += 'dddd'

def test_namedIndex_built_ins_representations():
    idx, vals = _create_namedIndex()
    print(idx)
    print(str(idx))
    print(repr(idx))

def test_namedIndex_built_ins_numpy_interfaces():
    idx, vals = _create_namedIndex()

    assert np.all(np.append(idx, 'ff') == np.append(vals, 'ff'))
    assert np.all(np.append(idx, ['ff', 'gg']) == np.append(vals, ['ff', 'gg']))
    assert np.all(np.insert(idx, 1, 'ff') == np.insert(vals, 1, 'ff'))
    assert np.all(np.insert(idx, [2,3], ['ee','gg']) == np.insert(vals, [2,3], ['ee','gg']))
    assert np.all(np.delete(idx, -1) == np.delete(vals, -1))
    assert np.all(np.delete(idx, [0,2]) == np.delete(vals, [0,2]))
    assert len(np.delete(idx,[0,1,2,3])) == 0

    with pytest.raises(KeyError): np.insert(idx, -1, 'a')

    assert np.all(np.array(idx) == vals)

def test_namedIndex_built_ins_pkls():
    idx, vals = _create_namedIndex()
    assert np.all(idx == pkl.loads(idx.dumps()))

def test_namedIndex_properties_names():
    idx, vals = _create_namedIndex()

    assert np.all(idx.names.astype(str) == list(vals))

    cidx = deepcopy(idx)
    cidx.names = np.hstack((vals[[2,1,0,3]], 'eee'))
    assert np.all(cidx[:-1] == vals[[2,1,0,3]])

    with pytest.raises(KeyError): cidx.names = ['a', 'a', 'b', 'c']

def test_namedIndex_properties_sizes():
    idx, vals = _create_namedIndex()
    assert idx.size == len(idx) == len(vals)
    assert idx.shape == vals.shape
    assert idx.ndim == 1

def test_namedIndex_methods_stats():
    idx, vals = _create_namedIndex()
    assert np.all(NamedIndex.uniquenames(vals[[0, 0, 1, 2, 3, 3, 3]], suffix = '_{}') == ['a', 'a_1', 'bbb', 'cc', 'dddd', 'dddd_1', 'dddd_2'])

def test_namedIndex_methods_indexing():
    idx, vals = _create_namedIndex()

    assert idx.namesof(1) == 'bbb'
    assert idx.namesof(-1) == 'dddd'
    assert np.all(idx.namesof([0,'cc']) == vals[[0,2]])
    with pytest.raises(IndexError): idx.namesof([4,5])

    assert isinstance(idx.idsof('cc'), int) and idx.idsof('cc') == 2
    assert np.all(idx.idsof(['a', 'dddd']) == [0,3])
    assert np.all(idx.idsof([0, 'dddd']) == [0,3])
    assert idx.idsof(['a', 'b', 'cc'], safe = True) == [0, None, 2]
    with pytest.raises(KeyError): idx.idsof(['a', 'b', 'cc'])

def test_namedIndex_methods_manipulations():
    idx, vals = _create_namedIndex()

    assert np.all(idx.take([0,2]) == ['a', 'cc'])
    assert np.all(idx.take(1) == 'bbb')
    assert np.all(idx.take('bbb') == 'bbb')
    assert np.all(idx.take(slice(1,-1)) == ['bbb', 'cc'])
    assert np.all(idx.take([True, False, True, False]) == ['a', 'cc'])
    with pytest.raises(IndexError): idx.take((0,1))

    assert np.all(idx.put(1, 'bb') == ['a', 'bb', 'cc', 'dddd'])
    assert np.all(idx.put([0,2], iter(['1','2'])) == ['1', 'bbb', '2', 'dddd'])
    assert np.all(idx.put(['a', 'cc'], ['c', 'aa']) == ['c', 'bbb', 'aa', 'dddd'])
    assert np.all(idx.put(slice(1,-1), ['3', '4']) == ['a', '3', '4', 'dddd'])
    assert np.all(idx.put([False, True, False, True], ['5', '6']) == ['a', '5', 'cc', '6'])
    with pytest.raises(TypeError): idx.put(1, ['b', 'c'])
    with pytest.raises(KeyError): idx.put(1, 'a')
    assert np.all(idx.put(0, 'a') == idx)

    cidx = deepcopy(idx)
    cidx.put(['bbb', 2, -1], ['b', 'c', 'd'], inline = True)
    assert np.all(cidx == ['a', 'b', 'c', 'd'])

    assert np.all(idx.append('ee') == np.hstack((vals, 'ee')))
    assert np.all(idx.append(['ff', 'gg']) == list(vals) + ['ff', 'gg'])
    with pytest.raises(KeyError): idx.append(idx)

    assert np.all(idx.insert(1, 'ee') == np.insert(vals, 1, 'ee'))
    assert np.all(idx.insert([0, 2], ['ff', 'gg']) == np.insert(vals, [0,2], ['ff', 'gg']))
    assert np.all(idx.insert(['a','cc'], ['ff', 'gg']) == np.insert(vals, [0,2], ['ff', 'gg']))
    assert np.all(idx.insert(1, ['ff', 'gg']) == np.insert(vals, 1, ['ff', 'gg']))
    assert np.all(idx.insert(1, NamedIndex(['ff', 'gg'])) == np.insert(vals, 1, ['ff', 'gg']))
    assert np.all(idx.insert(None, 'ee') == idx.append('ee'))
    with pytest.raises(KeyError): idx.insert(1, idx)

    assert np.all(idx.delete(-1) == vals[:-1])
    assert np.all(idx.delete(['a', 'dddd']) == vals[1:3])
    assert np.all(idx.delete([0,2]) == vals[[1,3]])
    assert len(idx.delete([True, False, False, False])) == 3
    assert len(idx.delete(slice(None))) == 0

    assert np.all(idx == vals)

def test_namedIndex_methods_converts():
    idx, vals = _create_namedIndex()
    assert np.all(idx.tolist() == vals)
    print(idx.tostring())

def test_namedIndex_methods_copy():
    idx, vals = _create_namedIndex()
    assert np.all(idx == idx.copy())
    assert idx is not idx.copy()
