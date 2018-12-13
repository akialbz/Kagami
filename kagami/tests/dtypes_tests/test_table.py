#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
test_core_dtypes_table

author(s): Albert (aki) Zhou
origin: 08-20-2018

"""


import os, pytest
import cPickle as cp
import numpy as np
from copy import deepcopy
from kagami.core import na, isna, Metadata
from kagami.dtypes import Table


# table
def _create_table():
    table = Table(np.arange(50).reshape((5,10)), dtype = int,
                  rownames = map(lambda x: 'row_%d' % x, range(5)), colnames = map(lambda x: 'col_%d' % x, range(10)),
                  rowindex = {'type': ['a', 'a', 'b', 'a', 'c'], 'order': [2, 1, 3, 5, 4]},
                  colindex = {'gene': map(lambda x: 'gid_%d' % x, range(10))},
                  metadata = {'name': 'test_table', 'origin': None, 'extra': Metadata(val1 = 1, val2 = 2)})
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

    with pytest.raises(KeyError): Table(np.arange(12).reshape((3,4)), rownames = ['a', 'b', 'a'], colnames = ['1', '2', '1', '1'])
    tab = Table(np.arange(12).reshape((3,4)), rownames = ['a', 'b', 'a'], colnames = ['1', '2', '1', '1'], fixRepeat = True)
    assert np.all(tab.rownames == ['a', 'b', 'a.2'])
    assert np.all(tab.colnames == ['1', '2', '1.2', '1.3'])

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
    assert ctable == table
    ctable[[1,2],[3,4]] = table[['row_1','row_2'],['col_3','col_4']]
    assert ctable == table
    ctable[ctable < 10] = 0
    assert np.all(ctable[0] == 0) and not np.any(ctable[1:] == 0)

    ctable[1,:] = na
    assert np.all(isna(ctable.X_[1])) # table is always 2-dimensional
    ctable = ctable.astype(float)
    ctable[1,:] = na
    assert np.all(np.isnan(ctable.X_[1]))
    ctable[:,2] = na
    assert np.all(np.isnan(ctable.X_[:,2]))
    ctable = ctable.astype(str)
    ctable[:,2] = na
    assert np.all(ctable.X_[:,2] == '')

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

    assert np.all((table < 10) == (dm < 10))
    assert np.all((table > 10) == (dm > 10))
    assert np.all((table <= 10) == (dm <= 10))
    assert np.all((table >= 10) == (dm >= 10))

    # arithmetic oprtations
    assert table[:2] + table[2:] == table
    ctable = deepcopy(table)[:-1]
    ctable += table[-1]
    assert ctable == table

    ctable = deepcopy(table)
    ctable.colnames = map(lambda x: 'ext_col_%d' % x, range(10))
    ctable.colindex = {'metabolite': map(lambda x: 'mid_%d' % x, range(10))}

    with pytest.raises(IndexError): table + ctable
    ctable.colnames = na
    with pytest.raises(IndexError): table + ctable
    ctable.colindex = na
    with pytest.raises(KeyError): table + ctable
    ctable.rownames = map(lambda x: 'ext_row_%d' % x, range(5))

    assert np.all((table + ctable).values == np.vstack((dm, dm)))
    ctable += table
    assert np.all(ctable.values == np.vstack((dm, dm)))

    # representation oprtations
    print table
    print str(table)
    print repr(table)

    # numpy array interface
    assert np.all(np.array(table) == table.values) and np.all(np.array(table) == dm)

    # pickle
    assert table == cp.loads(cp.dumps(table))

def test_table_properties():
    table = _create_table()
    dm = np.arange(50).reshape((5,10))

    # values and dtype
    ctable = deepcopy(table)
    assert np.all(ctable.values == dm)
    assert np.all(ctable.X_ == dm)
    ctable.X_ += 1
    assert np.all(ctable.values == np.arange(50).reshape((5,10)) + 1)
    assert ctable.dtype.kind == 'i'
    ctable.dtype = float
    assert ctable.dtype.kind == 'f'

    # names
    ctable = deepcopy(table)
    assert np.all(ctable.rownames == map(lambda x: 'row_%d' % x, range(5)))
    assert np.all(ctable.colnames == map(lambda x: 'col_%d' % x, range(10)))
    ctable.rownames = map(lambda x: 'new_row_%d' % x, range(5))
    ctable.colnames = map(lambda x: 'new_col_%d' % x, range(10))
    assert np.all(ctable.rownames == map(lambda x: 'new_row_%d' % x, range(5)))
    assert np.all(ctable.colnames == map(lambda x: 'new_col_%d' % x, range(10)))

    # index
    ctable = deepcopy(table)
    assert np.all(ctable.rowindex['type'] == ['a', 'a', 'b', 'a', 'c']) and np.all(ctable.rowindex['order'] == [2, 1, 3, 5, 4])
    assert np.all(ctable.colindex['gene'] == map(lambda x: 'gid_%d' % x, range(10)))
    ctable.rowindex = {'new_type': ['a', 'b', 'c', 'd', 'e'], 'new_order': [1, 2, 3, 4, 5]}
    ctable.colindex = [('feature', map(lambda x: 'feat_%d' % x, range(10))), ('normal', np.ones(10, dtype = bool))]
    assert np.all(ctable.rowindex['new_type'] == ['a', 'b', 'c', 'd', 'e']) and np.all(ctable.rowindex['new_order'] == [1, 2, 3, 4, 5])
    assert np.all(ctable.colindex['feature'] == map(lambda x: 'feat_%d' % x, range(10))) and np.all(ctable.colindex['normal'] == True)

    # metadata
    assert table.metadata['name'] == 'test_table' and table.metadata['origin'] is None
    assert table.metadata.name == 'test_table' and table.metadata.origin is None
    table.metadata['name'] = 'new_test_table'
    table.metadata.normal = True
    table.metadata.newval = 123
    assert table.metadata.name == 'new_test_table' and table.metadata['normal'] == True and table.metadata['newval'] == 123

    # transpose
    ctable = table.T
    assert ctable.shape == (10,5)
    assert np.all(ctable.values == table.values.T)
    assert np.all(ctable.rownames == table.colnames) and np.all(ctable.colnames == table.rownames)
    assert ctable.rowindex == table.colindex and ctable.colindex == table.rowindex
    assert set(ctable.metadata.keys()) == set(table.metadata.keys())

    # sizes
    assert table.nrow == 5
    assert table.ncol == 10
    assert table.size == 5
    assert table.shape == (5,10)
    assert table.ndim == 2

    # fixRepeat
    assert table.fixRepeat == False
    table.fixRepeat = True
    table = table[[0, 1, 1, 3, 4], [0, 1, 2, 0, 1, 2, 0, 1, 2, 0]]
    assert np.all(table.rownames == ['row_0', 'row_1', 'row_1.2', 'row_3', 'row_4'])
    assert np.all(table.colnames == ['col_0', 'col_1', 'col_2', 'col_0.2', 'col_1.2', 'col_2.2', 'col_0.3', 'col_1.3', 'col_2.3', 'col_0.4'])

def test_table_methods():
    table = _create_table()

    # manipulations
    assert table[:2] + table[2:] == table
    assert table[:2].append(table[2:], axis = 0) == table
    assert table[:,:2].append(table[:,2:], axis = 1) == table
    assert table[:,:-1].append(table[:,-1], axis = 1) == table

    assert table[['row_0', 'row_3', 'row_4'],:].insert(table[['row_1', 'row_2']], 1, axis = 0) == table
    assert table[:,[0,1,4]].insert(table[:,[2,3]], 2, axis = 1) == table[:,:5]
    assert table[:,:2].insert(table[:,2:], axis = 1) == table

    assert np.all(table.drop(-1, axis = 0).rownames == ['row_0', 'row_1', 'row_2', 'row_3'])
    assert np.all(table.drop([1,2], axis = 1).colnames == ['col_%d' % i for i in range(10) if i not in (1,2)])
    assert np.all(table.drop(slice(1,-1), axis = 1).colnames == ['col_0', 'col_9'])

    # copy
    assert table == table.copy()
    assert table is not table.copy()

    # converts
    ctable = table.astype(float)
    assert ctable.dtype.kind == 'f'
    assert np.all(np.isclose(ctable.values, table.values))

    sdm = np.array(
        [[       '',        '', '<gene>', 'gid_0', 'gid_1', 'gid_2', 'gid_3', 'gid_4', 'gid_5', 'gid_6', 'gid_7', 'gid_8', 'gid_9'],
         [ '<type>', '<order>',      '#', 'col_0', 'col_1', 'col_2', 'col_3', 'col_4', 'col_5', 'col_6', 'col_7', 'col_8', 'col_9'],
         [      'a',       '2',  'row_0',     '0',     '1',     '2',     '3',     '4',     '5',     '6',     '7',     '8',     '9'],
         [      'a',       '1',  'row_1',    '10',    '11',    '12',    '13',    '14',    '15',    '16',    '17',    '18',    '19'],
         [      'b',       '3',  'row_2',    '20',    '21',    '22',    '23',    '24',    '25',    '26',    '27',    '28',    '29'],
         [      'a',       '5',  'row_3',    '30',    '31',    '32',    '33',    '34',    '35',    '36',    '37',    '38',    '39'],
         [      'c',       '4',  'row_4',    '40',    '41',    '42',    '43',    '44',    '45',    '46',    '47',    '48',    '49']]
    )

    assert np.all(np.array(table.tolist(), dtype = str) == sdm[1:,2:])
    assert np.all(np.array(table.tolist(withindex = True), dtype = str) == sdm)

    print table.tostr(delimiter = '\t', transpose = True, withindex = True)

    # portals
    fname = 'test_table'

    table.savecsv(fname + '.csv')
    ltable = Table.loadcsv(fname + '.csv')
    print ltable
    assert ltable == table
    if os.path.isfile(fname + '.csv'): os.remove(fname + '.csv')

    table.savehdf(fname + '.hdf', compression = 9)
    ltable = Table.loadhdf(fname + '.hdf')
    print ltable
    assert ltable == table
    if os.path.isfile(fname + '.hdf'): os.remove(fname + '.hdf')

    table.saverdata(fname + '.rdata', dname = 'data', rowindex = 'row.index', colindex = 'col.index')
    ltable = Table.loadrdata(fname + '.rdata', dname = 'data', rowindex = 'row.index', colindex = 'col.index')
    print ltable
    assert ltable == table
    if os.path.isfile(fname + '.rdata'): os.remove(fname + '.rdata')

