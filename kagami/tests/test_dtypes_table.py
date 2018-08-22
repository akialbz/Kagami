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
from kagami.dtypes import factor, _Index, Table


# index
def _create_index():
    Color = factor('Color', ['r', 'g', 'b'])
    return _Index(color = Color(arrValues = [1, 1, 0, 1, 2, 0]), index = np.arange(6), names = map(lambda x: 'n%d' % x, range(6)))

def test_index_creation():
    with pytest.raises(Exception): _Index()
    idx = _Index(size = 6)
    idx = _Index(color = [u'value'] * 6, index = np.arange(6), names = map(lambda x: 'n%d' % x, range(6)))
    idx = _Index(idx)
    assert cp.loads(cp.dumps(idx)) == idx

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

    # eq & ne
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

    # tolist
    lst1 = idx1.toList(transpose = True)
    assert np.all(lst1[0] == ['color', 'index', 'names'])
    assert np.all(lst1[-1] == ['r', 5, 'n5'])

    # copy
    assert deepcopy(idx1) == idx1.copy()


# table
def _create_table():
    table = Table(np.arange(50).reshape((5,10)), dtype = int,
                  rownames = map(lambda x: 'row_%d' % x, range(5)), colnames = map(lambda x: 'col_%d' % x, range(10)),
                  rowindex = {'type': ['a', 'a', 'b', 'a', 'c'], 'index': np.arange(5)+1},
                  colindex = {'feature': map(lambda x: 'gene_%d' % x, range(10))},
                  metadata = {'name': 'test_table'})
    return table

def test_table_creation():
    table = Table(np.arange(50).reshape((5,10)), dtype = int)
    assert np.all(table == np.loads(cp.dumps(table)))

def test_table_built_ins():
    table = _create_table()
    dm = np.arange(50).reshape((5,10))

    # getitem & setitem
    assert np.all(table[[0,2,4]].values == dm[[0,2,4]])
    assert np.all(table[:,[1,3,5,7]].values == dm[:,[1,3,5,7]])
    assert np.all(table[[0,-1],[7,8]].values == dm[np.ix_([0,-1],[7,8])])
    assert np.all(table[['row_1', 'row_3'], ['col_2', 'col_4', 'col_6']].values == dm[np.ix_([1,3],[2,4,6])])
    assert np.all(table[np.array([1,0,1,0,1], dtype = bool)].rownames == ['row_0', 'row_2', 'row_4'])
    assert np.all(table[:,np.array([0,0,1,0,0,1,0,0,0,1], dtype = bool)].colindex['feature'] == map(lambda x: 'gene_%d' % x, [2,5,9]))

    ntable = deepcopy(table)
    ntable.rownames = map(lambda x: 'new_row_%d' % x, range(5))
    table[[1,3]] = ntable[[2,4]]
    assert np.all(table.rownames == ['row_0', 'new_row_2', 'row_2', 'new_row_4', 'row_4'])

    #
    # def __getitem__(self, item):
    #     rids, cids = self._parseIndices(item)
    #     return Table(self._dmatx[np.ix_(rids,cids)], dtype = self._dtype, metadata = self._metas,
    #                  rownames = self.rownames[rids], colnames = self.colnames[cids],
    #                  rowindex = self.rowindex[rids], colindex = self.colindex[cids])
    #
    # def __setitem__(self, key, value):
    #     rids, cids = self._parseIndices(key)
    #     if isinstance(value, Table):
    #         self._dmatx[np.ix_(rids,cids)] = value.values
    #
    #         if hasvalue(self._rndct):
    #             if isna(value._rndct): raise KeyError('input table does not have row names')
    #             nams = self.rownames
    #             nams[rids] = value.rownames
    #             self.rownames = nams
    #         if hasvalue(self._cndct):
    #             if isna(value._cndct): raise KeyError('input table does not have column names')
    #             nams = self.colnames
    #             nams[cids] = value.colnames
    #             self.colnames = nams
    #
    #         self.rowindex[rids] = value.rowindex
    #         self.colindex[cids] = value.colindex
    #     else:
    #         self._dmatx[np.ix_(rids,cids)] = value
    #
    # def __add__(self, other):
    #     return Table.vstack(self, other)
    #
    # def __eq__(self, other):
    #     if isinstance(other, Table):
    #         return self._dmatx == other.values
    #     elif isinstance(other, np.ndarray):
    #         return self._dmatx == other
    #     else: raise TypeError('comparison not supported')
    #
    # def __len__(self):
    #     return self.nrow
    #
    # def __str__(self):
    #     slns = self.toStr(delimiter = '\t', withIndex = True, asLines = True)
    #     if len(slns) > 20: slns = slns[:15] + ['', '...', ''] + slns[-2:]
    #     slns += ['table([%s], shape = (%d x %d))' % (str(self._dtype), self.nrow, self.ncol)]
    #     return join(slns, '\n')
    #
    # def __repr__(self):
    #     return self.__str__()
    #
    # def __array__(self):
    #
    #
    #
    #
