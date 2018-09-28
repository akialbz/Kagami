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
from kagami.dtypes import Table


# table
def _create_table():
    table = Table(np.arange(50).reshape((5,10)), dtype = int,
                  rownames = map(lambda x: 'row_%d' % x, range(5)), colnames = map(lambda x: 'col_%d' % x, range(10)),
                  rowindex = {'type': ['a', 'a', 'b', 'a', 'c'], 'order': [2, 1, 3, 5, 4]},
                  colindex = {'gene': map(lambda x: 'gid_%d' % x, range(10))},
                  metadata = {'name': 'test_table', 'origin': None})
    return table

def test_table_creation():
    Table(np.arange(30).reshape((5,6)), dtype = float)
    Table([np.arange(10)])
    Table([[0, 1, 1, 0, 1], [1, 1, 0, 1, 0]], dtype = bool)
    Table(np.arange(30).reshape((5,6)), rownames = ['a', 'b', 'c', 'd', 'e'], rowindex = {'order': np.arange(5)})
    Table(np.arange(30).reshape((5,6)), colnames = ['1', '2', '3', '4', '5', '6'], colindex = {'feat': map(str,np.arange(6))})

    with pytest.raises(ValueError): Table(np.arange(10))
    with pytest.raises(ValueError): Table(np.arange(30).reshape((5,6)), rownames = ['a', 'b', 'c'])
    with pytest.raises(ValueError): Table(np.arange(30).reshape((5,6)), colindex = {'order': range(10)})

def test_table_built_ins():
    table = _create_table()
    dm = np.arange(50).reshape((5,10))

    # item oprtations
    assert np.all(table == dm)
    assert np.all(table[1:,:-1] == dm[1:,:-1])
    assert np.all(table[[0,2,4]].rownames == ['row_0', 'row_2', 'row_4'])
    assert np.all(table[:,[1,3,5,7,9]].colnames == ['col_1', 'col_3', 'col_5', 'col_7', 'col_9'])
    assert np.all(table[[0,2],[1,5]].rowindex['type'] == ['a', 'b'])
    assert np.all(table[[False,False,True,True,False],1:5].colindex['gene'] == map(lambda x: 'gid_%d' % x, [1,2,3,4]))
    assert np.all(table[['row_1' ,'row_3'], ['col_2', 'col_4', 'col_6']] == dm[np.ix_([1,3],[2,4,6])])
    assert np.all(table[1,1].shape == (1,1))

    ctable = deepcopy(table)
    ctable['row_0'] = 0
    assert np.all(ctable[0] == np.zeros(10))
    ctable[:,'col_2'] = 1
    assert np.all(ctable[:,2] == np.ones(5))
    ctable[[1,2],[3,4]] = np.array([[5,6],[7,8]])
    assert np.all(ctable.values[np.ix_([1,2],[3,4])] == [[5,6],[7,8]])
    ctable[:] = dm
    assert np.all(ctable == table)

    ctable = deepcopy(table)
    del ctable['row_2']
    assert np.all(ctable.rownames == ['row_0', 'row_1', 'row_3', 'row_4'])
    assert ctable.shape == (4,10)
    del ctable[:,'col_4']
    assert np.all(ctable.colindex['gene'] == ['gid_%d' % i for i in range(10) if i != 4])
    assert ctable.shape == (4,9)
    del ctable[-1:,3:]
    assert ctable.shape == (3,3)
    del ctable[:]
    assert ctable.shape == (0,0)
    assert np.all(ctable.rowindex.names == ['type', 'order'])
    assert np.all(ctable.colindex.names == ['gene'])

    # sequence oprtations
    assert all([np.all(tl == dl) for tl,dl in zip(table,dm)])
    assert 0 in table
    assert 100 not in table
    assert len(table) == 5

    # comparison oprtations
    assert np.all(table == dm)
    assert np.all((table == 5) == (dm == 5))
    assert table == deepcopy(table)
    assert table != Table(dm, dtype = int)

    # arithmetic oprtations
    assert table[:2] + table[2:] == table
    ctable = deepcopy(table)[:-1]
    ctable += table[-1]
    assert ctable == table

