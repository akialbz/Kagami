#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
test_dtypes_namedIndex

author(s): Albert (aki) Zhou
origin: 08-23-2018

"""


import pytest
import cPickle as cp
import numpy as np
from string import ascii_lowercase
from copy import deepcopy
from kagami.dtypes import NamedIndex


def _create_namedIndex():
    vals = ['a', 'bbb', 'cc', 'dddd']
    return NamedIndex(vals), np.array(vals)

def test_namedIndex_creation():
    NamedIndex()
    NamedIndex('aa')
    NamedIndex(['aa'])
    NamedIndex(['a', u'b', 'cc'])

    with pytest.raises(TypeError): NamedIndex(['a', ['b', 'c']])
    with pytest.raises(KeyError): NamedIndex(['a', 'a', 'b'])

    idx = NamedIndex(['a', 'a', 'b'], fixRepeat = True)
    assert np.all(idx == ['a', 'a.2', 'b'])
    assert np.all(idx == NamedIndex(idx))

    print '\n', repr(NamedIndex(['%s%d' % (c,n) for c in ascii_lowercase for n in range(5)]))

def test_namedIndex_built_ins():
    idx, vals = _create_namedIndex()

    # item oprtations
    assert np.all(idx[:3] == vals[:3])
    assert np.all(idx[-1] == NamedIndex('dddd'))
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

    with pytest.raises(KeyError): cidx[1] = 'a'
    with pytest.raises(TypeError): cidx[:] = 1

    cidx = deepcopy(idx)
    del cidx[[1,2]]
    assert np.all(cidx == ['a', 'dddd'])
    del cidx[-1]
    assert np.all(cidx == NamedIndex('a'))

    # sequence oprtations
    assert np.all(vals == [n for n in idx])
    assert 'a' in idx
    assert 'aa' not in idx
    assert 'a' not in idx[1:]
    assert len(idx) == vals.shape[0]
    assert len(idx[-1]) == len(vals[-1])

    # comparison oprtations
    assert np.all(idx == vals)
    assert np.all((idx == 'a') == [True, False, False, False])
    assert np.sum(idx == np.array('abc')) == 0
    assert np.sum(idx == NamedIndex(['bbb'])) == 1

    # arithmetic oprtations
    assert np.all(idx + ['ee', 'fff'] == np.hstack((vals, ['ee', 'fff'])))
    assert np.all(idx[[0,2]] + idx[[1,3]] == idx[[0,2,1,3]])
    assert np.all(idx == vals)

    cidx = deepcopy(idx)
    cidx += 'eee'
    assert np.all(cidx == idx + ['eee'])
    cidx += np.array(['ff', 'gg'])
    assert np.all(cidx == idx + ['eee', 'ff', 'gg'])

    with pytest.raises(KeyError): cidx += ['dddd']

    # representation oprtations
    print idx
    print str(idx)
    print repr(idx)

    # numpy array interface
    assert np.all(np.insert(idx, 1, 'ff') == np.insert(vals, 1, 'ff'))
    assert np.all(np.insert(idx, [2,3], ['ee','gg']) == np.insert(vals, [2,3], ['ee','gg']))
    assert np.all(np.delete(idx, -1) == np.delete(vals, -1))
    assert np.all(np.delete(idx, [0,2]) == np.delete(vals, [0,2]))
    assert len(np.delete(idx,[0,1,2,3])) == 0

    with pytest.raises(KeyError): np.insert(idx, -1, 'a')

    # pickle
    assert np.all(idx == cp.loads(cp.dumps(idx)))

def test_namedIndex_properties():
    idx, vals = _create_namedIndex()

    # names
    assert np.all(idx.names.astype(str) == list(vals))

    cidx = deepcopy(idx)
    cidx.names = np.hstack((vals[[2,1,0,3]], 'eee'))
    assert np.all(cidx[:-1] == vals[[2,1,0,3]])

    with pytest.raises(KeyError): cidx.names = ['a', 'a', 'b', 'c']

    # sizes
    assert idx.size == len(idx) == len(vals)
    assert idx.shape == vals.shape
    assert idx.ndim == 1

    # fixRepeat
    assert idx.fixRepeat == False
    idx.fixRepeat = True
    idx = idx[[0, 0, 1, 2, 3]]
    assert np.all(idx == ['a', 'a.2', 'bbb', 'cc', 'dddd'])

def test_namedIndex_methods():
    idx, vals = _create_namedIndex()

    # indexing
    assert idx.namesof(1) == 'bbb'
    assert idx.namesof(-1) == 'dddd'
    assert np.all(idx.namesof([0,2]) == vals[[0,2]])
    with pytest.raises(IndexError): idx.namesof([4,5])

    assert isinstance(idx.idsof('cc'), int) and idx.idsof('cc') == 2
    assert np.all(idx.idsof(['a', 'dddd']) == [0,3])
    with pytest.raises(KeyError): idx.idsof(['a', 'b', 'cc'])

    # manipulations
    assert np.all(idx.append('ee') == np.hstack((vals, 'ee')))
    assert np.all(idx.append(['ff', 'gg']) == list(vals) + ['ff', 'gg'])
    with pytest.raises(KeyError): idx.append(idx)

    assert np.all(idx.insert('ee', 1) == np.insert(vals, 1, 'ee'))
    assert np.all(idx.insert(['ff', 'gg'], [0,2]) == np.insert(vals, [0,2], ['ff', 'gg']))
    assert np.all(idx.insert(['ff', 'gg'], ['a','cc']) == np.insert(vals, [0,2], ['ff', 'gg']))
    assert np.all(idx.insert(NamedIndex(['ff', 'gg']), 1) == np.insert(vals, 1, ['ff', 'gg']))
    assert np.all(idx.insert(['ee']) == idx.append('ee'))
    with pytest.raises(KeyError): idx.insert(idx, 1)

    assert np.all(idx.drop(-1) == vals[:-1])
    assert np.all(idx.drop(['a', 'dddd']) == vals[1:3])
    assert np.all(idx.drop([0,2]) == vals[[1,3]])
    assert len(idx.drop([0,1,2,3])) == 0

    assert np.all(idx == vals)

    # copy
    assert np.all(idx == idx.copy())
    assert idx is not idx.copy()
