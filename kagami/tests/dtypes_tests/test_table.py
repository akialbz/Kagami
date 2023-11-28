#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
test_core_dtypes_table

author(s): Albert (aki) Zhou
added: 08-20-2018

"""


import os, pytest
import pickle as pkl
import numpy as np
import pandas as pd
from copy import deepcopy
from kagami.comm import smap, Metadata
from kagami.dtypes import NamedIndex, Table


# table
def _create_table():
    table = Table(np.arange(50).reshape((5,10)), dtype = int,
                  rownames = map(lambda x: 'row_%d' % x, range(5)),
                  colnames = map(lambda x: 'col_%d' % x, range(10)),
                  rowindex = {'type': ['a', 'a', 'b', 'a', 'c'], 'order': [2, 1, 3, 5, 4]},
                  colindex = [('gene', map(lambda x: 'gid_%d' % x, range(10)))],
                  metadata = {'name': 'test_table', 'origin': None, 'extra': Metadata(val1 = 1, val2 = 2)})
    return table

def test_table_creation():
    Table(np.arange(30).reshape((5,6)), dtype = float)
    Table([np.arange(10)])
    Table([[0, 1, 1, 0, 1], [1, 1, 0, 1, 0]], dtype = bool)
    Table(np.arange(30).reshape((5,6)), rownames = ['a', 'b', 'c', 'd', 'e'], rowindex = {'order': np.arange(5)})
    Table(np.arange(30).reshape((5,6)), colnames = ['1', '2', '3', '4', '5', '6'], colindex = {'feat': map(str,np.arange(6))})

    fname = 'test_table_memmap'
    Table(np.arange(30).reshape((5,6)), colnames = ['1', '2', '3', '4', '5', '6'], colindex = {'feat': map(str,np.arange(6))}, memmap = fname)
    if os.path.isfile(fname): os.remove(fname)

    with pytest.raises(ValueError): Table(np.arange(10))
    with pytest.raises(ValueError): Table(np.arange(30).reshape((5,6)), rownames = ['a', 'b', 'c'])
    with pytest.raises(ValueError): Table(np.arange(30).reshape((5,6)), colindex = {'order': range(10)})

    with pytest.raises(KeyError): Table(np.arange(12).reshape((3,4)), rownames = ['a', 'b', 'a'], colnames = ['1', '2', '1', '1'])
    tab = Table(np.arange(12).reshape((3,4)),
                rownames = NamedIndex.uniquenames(['a', 'b', 'a']),
                colnames = NamedIndex.uniquenames(['1', '2', '1', '1']))
    assert np.all(tab.rownames == ['a', 'b', 'a.1'])
    assert np.all(tab.colnames == ['1', '2', '1.1', '1.2'])

def test_table_built_ins_item_oprtations():
    table = _create_table()
    dm = np.arange(50).reshape((5,10))

    assert np.all(table == dm)
    assert np.all(table[1:,:-1] == dm[1:,:-1])
    assert np.all(table[1] == np.arange(10)+10)
    assert np.all(table[:,-1] == np.array([9,19,29,39,49]).reshape((-1,1)))
    assert np.all(table[[0,2,4]].rownames == ['row_0', 'row_2', 'row_4'])
    assert np.all(table[:,[1,3,5,7,9]].colnames == ['col_1', 'col_3', 'col_5', 'col_7', 'col_9'])
    assert np.all(table[:,NamedIndex(['col_2', 'col_4', 'col_6'])] == dm[:,[2,4,6]])
    assert np.all(table[[0,2],[1,5]].rowindex['type'] == ['a', 'b'])
    assert np.all(table[[False,False,True,True,False],1:5].colindex.gene == list(map(lambda x: 'gid_%d' % x, [1,2,3,4])))
    assert np.all(table[['row_1' ,'row_3'], ['col_2', 'col_4', 'col_6']] == dm[np.ix_([1,3],[2,4,6])])
    assert np.all(table[1,1].shape == (1,1))

    ctable = deepcopy(table)
    ctable['row_0'] = 0
    assert np.all(ctable[0] == np.zeros(10))
    ctable['row_0'] = iter([1,2,3,4,5,6,7,8,9,10])
    assert np.all(ctable[0] == np.arange(10)+1)
    ctable[:,'col_2'] = 1
    assert np.all(ctable[:,2] == np.ones((5,1)))
    ctable[:,'col_2'] = np.array([5,4,3,2,1]).reshape((-1,1))
    assert np.all(ctable[:,2] == (5-np.arange(5)).reshape((-1,1)))
    ctable[[1,2],[3,4]] = np.array([[5,6],[7,8]])
    assert np.all(ctable.values[np.ix_([1,2],[3,4])] == [[5,6],[7,8]])
    ctable[:] = dm
    assert ctable == table
    ctable[[1,2],[3,4]] = table[['row_1','row_2'],['col_3','col_4']]
    assert ctable == table
    ctable[ctable < 10] = 0
    assert np.all(ctable[0] == 0) and not np.any(ctable[1:] == 0)

    ctable = ctable.astype(float)
    ctable[1,:] = np.nan
    assert np.all(np.isnan(ctable.X_[1]))
    ctable[:,2] = np.nan
    assert np.all(np.isnan(ctable.X_[:,2]))

    ctable = deepcopy(table)
    del ctable['row_2']
    assert np.all(ctable.rows_ == ['row_0', 'row_1', 'row_3', 'row_4'])
    assert ctable.shape == (4,10)
    del ctable[:,'col_4']
    assert np.all(ctable.cidx_['gene'] == ['gid_%d' % i for i in range(10) if i != 4])
    assert ctable.shape == (4,9)
    del ctable[-1:]
    assert ctable.shape == (3,9)
    del ctable[:,-3:]
    assert ctable.shape == (3,6)

    ctable = deepcopy(table)
    del ctable[None]
    assert ctable.shape == (0,0)

    ctable = deepcopy(table)
    del ctable[:]
    assert ctable.shape == (0,0)
    assert np.all(ctable.ridx_.names == ['type', 'order'])
    assert np.all(ctable.cidx_.names == ['gene'])

def test_table_built_ins_seq_oprtations():
    table = _create_table()
    dm = np.arange(50).reshape((5,10))
    assert all([np.all(tl == dl) for tl,dl in zip(table,dm)])
    assert 0 in table
    assert 100 not in table
    assert len(table) == 5

def test_table_built_ins_comparisons():
    table = _create_table()
    dm = np.arange(50).reshape((5,10))

    assert np.all(table == dm)
    assert np.all((table == 5) == (dm == 5))
    assert table == deepcopy(table)
    assert table == Table(dm, dtype = int)
    assert table != Table(dm, dtype = int, rownames = ('a','b','c','d','e'))
    assert table != Table(dm, dtype = int, colindex = {'cids': [f'cc{i}' for i in range(10)]})

    assert np.all((table < 10) == (dm < 10))
    assert np.all((table > 10) == (dm > 10))
    assert np.all((table <= 10) == (dm <= 10))
    assert np.all((table >= 10) == (dm >= 10))

def test_table_built_ins_arithmetic_oprtations():
    table = _create_table()
    dm = np.arange(50).reshape((5,10))

    assert table[:2] + table[2:] == table
    ctable = deepcopy(table)[:-1]
    ctable += table[-1]
    assert ctable == table

    ctable = deepcopy(table)
    ctable.cols_ = map(lambda x: 'ext_col_%d' % x, range(10))
    ctable.cidx_ = {'metabolite': map(lambda x: 'mid_%d' % x, range(10))}

    with pytest.raises(IndexError): table + ctable
    ctable.cols_ = None
    with pytest.raises(IndexError): table + ctable
    ctable.cidx_ = None
    with pytest.raises(KeyError): table + ctable
    ctable.rows_ = map(lambda x: 'ext_row_%d' % x, range(5))
    assert np.all((table + ctable).values == np.vstack((dm, dm)))
    ctable += table
    assert np.all(ctable.values == np.vstack((dm, dm)))

def test_table_built_ins_representations():
    table = _create_table()
    print(table)
    print(str(table))
    print(repr(table))

def test_table_built_ins_numpy_interfaces():
    table = _create_table()
    dm = np.arange(50).reshape((5, 10))
    assert np.all(np.array(table) == table.values) and np.all(np.array(table) == dm)

def test_table_built_ins_pkls():
    table = _create_table()
    assert table == pkl.loads(pkl.dumps(table))

def test_table_properties_values():
    table = _create_table()
    dm = np.arange(50).reshape((5,10))

    ctable = deepcopy(table)
    assert np.all(ctable.values == dm)
    assert np.all(ctable.X_ == dm)
    ctable.X_ += 1
    assert np.all(ctable.values == np.arange(50).reshape((5,10)) + 1)
    assert ctable.dtype.kind == 'i'
    ctable.dtype = float
    assert ctable.dtype.kind == 'f'

def test_table_properties_names():
    table = _create_table()
    ctable = deepcopy(table)
    assert np.all(ctable.rownames == list(map(lambda x: 'row_%d' % x, range(5 ))))
    assert np.all(ctable.colnames == list(map(lambda x: 'col_%d' % x, range(10))))
    ctable.rows_ = map(lambda x: 'new_row_%d' % x, range(5))
    ctable.cols_ = map(lambda x: 'new_col_%d' % x, range(10))
    assert np.all(ctable.rownames == list(map(lambda x: 'new_row_%d' % x, range(5 ))))
    assert np.all(ctable.colnames == list(map(lambda x: 'new_col_%d' % x, range(10))))

def test_table_properties_index():
    table = _create_table()
    ctable = deepcopy(table)
    assert np.all(ctable.rowindex['type'] == ['a', 'a', 'b', 'a', 'c']) and np.all(ctable.rowindex['order'] == [2, 1, 3, 5, 4])
    assert np.all(ctable.colindex['gene'] == list(map(lambda x: 'gid_%d' % x, range(10))))
    ctable.ridx_ = {'new_type': ['a', 'b', 'c', 'd', 'e'], 'new_order': [1, 2, 3, 4, 5]}
    ctable.cidx_ = [('feature', map(lambda x: 'feat_%d' % x, range(10))), ('normal', np.ones(10, dtype = bool))]
    assert np.all(ctable.rowindex.new_type == ['a', 'b', 'c', 'd', 'e']) and np.all(ctable.rowindex['new_order'] == [1, 2, 3, 4, 5])
    assert np.all(ctable.colindex.feature  == list(map(lambda x: 'feat_%d' % x, range(10)))) and np.all(ctable.colindex['normal'] == True)

def test_table_properties_metadata():
    table = _create_table()
    assert table.metadata['name'] == 'test_table' and table.metadata['origin'] is None
    assert table.metadata.name == 'test_table' and table.metadata.origin is None
    table.metadata['name'] = 'new_test_table'
    table.metadata.normal = True
    table.metadata.newval = 123
    assert table.metadata.name == 'new_test_table' and table.metadata['normal'] == True and table.metadata['newval'] == 123

def test_table_properties_transpose():
    table = _create_table()
    ctable = table.T
    assert ctable.shape == (10,5)
    assert np.all(ctable.values == table.values.T)
    assert np.all(ctable.rows_ == table.cols_) and np.all(ctable.cols_ == table.rows_)
    assert ctable.rowindex == table.colindex and ctable.colindex == table.rowindex
    assert set(ctable.metadata.keys()) == set(table.metadata.keys())

def test_table_properties_sizes():
    table = _create_table()
    assert table.nrow == 5
    assert table.ncol == 10
    assert table.size == 5
    assert table.shape == (5,10)
    assert table.ndim == 2

def test_table_methods_manipulations():
    table = _create_table()

    assert table[:2] + table[2:] == table
    assert table[:2].append(table[2:], axis = 0) == table
    assert table[:,:2].append(table[:,2:], axis = 1) == table
    assert table[:,:-1].append(table[:,-1], axis = 1) == table

    assert table[['row_0', 'row_3', 'row_4'],:].insert(1, table[['row_1', 'row_2']], axis = 0) == table
    assert table[:,[0,1,4]].insert(2, table[:,[2,3]], axis = 1) == table[:,:5]
    assert table[:,:2].insert(None, table[:,2:], axis = 1) == table
    with pytest.raises(IndexError): table.insert(None, table[:,2:], axis = 2)

    ctable = deepcopy(table)
    ctable.rows_ = None
    ctable.cols_ = None
    assert ctable[[0,3,4],:].insert(1, ctable[np.array([1,2])], axis = 0) == ctable
    assert ctable[:,[0,1,4]].insert(2, ctable[:,np.array([2,3])], axis = 1) == ctable[:,:5]
    assert ctable[:,:2].insert(None, ctable[:,2:], axis = 1) == ctable
    with pytest.raises(IndexError): ctable.insert(None, ctable[:,2:], axis = 2)

    assert np.all(table.delete(-1, axis = 0).rownames == ['row_0', 'row_1', 'row_2', 'row_3'])
    assert np.all(table.delete([1,2], axis = 1).colnames == ['col_%d' % i for i in range(10) if i not in (1,2)])
    assert np.all(table.delete(slice(1,-1), axis = 1).colnames == ['col_0', 'col_9'])
    assert np.all(table.delete(None, axis = 0).rowindex.names == ['type', 'order'])
    assert np.all(table.delete(None, axis = 1).colindex.names == ['gene'])
    with pytest.raises(IndexError): table.delete([1,2], axis = 2)

def test_table_methods_copy():
    table = _create_table()
    assert table == table.copy()
    assert table is not table.copy()

def test_table_methods_converts():
    table = _create_table()

    ctable = table.astype(float)
    assert ctable.dtype.kind == 'f'
    assert np.all(np.isclose(ctable.values, table.values))

    idx = [[                           'gid_0', 'gid_1', 'gid_2', 'gid_3', 'gid_4', 'gid_5', 'gid_6', 'gid_7', 'gid_8', 'gid_9'],
           [                           'col_0', 'col_1', 'col_2', 'col_3', 'col_4', 'col_5', 'col_6', 'col_7', 'col_8', 'col_9']]
    dmx = [[    'a',     '2', 'row_0',     '0',     '1',     '2',     '3',     '4',     '5',     '6',     '7',     '8',     '9'],
           [    'a',     '1', 'row_1',    '10',    '11',    '12',    '13',    '14',    '15',    '16',    '17',    '18',    '19'],
           [    'b',     '3', 'row_2',    '20',    '21',    '22',    '23',    '24',    '25',    '26',    '27',    '28',    '29'],
           [    'a',     '5', 'row_3',    '30',    '31',    '32',    '33',    '34',    '35',    '36',    '37',    '38',    '39'],
           [    'c',     '4', 'row_4',    '40',    '41',    '42',    '43',    '44',    '45',    '46',    '47',    '48',    '49']]

    sdm = np.array(
        [[    '',      '', 'gene'] + idx[0],
         ['type', 'order',    '#'] + idx[1]] + dmx
    )
    ddm = np.array(
        [[           '',             '', '<gene::<U5>'] + idx[0],
         ['<type::<U1>', '<order::<i8>',  '#<::<i8::>'] + idx[1]] + dmx
    )

    assert np.all(table.tosarray(withdtype = False) == sdm)
    assert np.all(table.tosarray() == ddm)
    assert table == Table.fromsarray(ddm)

    assert np.all(np.array(table.tolist(), dtype = str) == ddm[2:,3:])
    print(table.tostring(delimiter = '\t', transpose = True, withindex = True))

    df = table.todataframe('idx')
    assert np.all(np.array(df.index.get_level_values('type'))  == table.ridx_.type)
    assert np.all(np.array(df.index.get_level_values('order')) == table.ridx_.order)
    assert np.all(np.array(df.index.get_level_values('idx'))  == np.array(table.rows_))
    assert np.all(np.array(df.columns.get_level_values('gene')) == table.cidx_.gene)
    assert np.all(np.array(df.columns.get_level_values('idx')) == np.array(table.cols_))
    assert np.all(np.isclose(df.to_numpy(), table.X_))

    assert isinstance(df.index,   pd.MultiIndex)
    assert isinstance(df.columns, pd.MultiIndex)
    table.ridx_ = table.cidx_ = None
    df = table.todataframe('idx')
    assert isinstance(df.index,   pd.Index)
    assert isinstance(df.columns, pd.Index)
    df = table.df
    assert isinstance(df.index,   pd.Index)
    assert isinstance(df.columns, pd.Index)

    ctable = deepcopy(table)
    ctable.rows_ = None
    ctable.cols_ = None
    df = ctable.todataframe('idx', multidx = True)
    assert np.all(np.array(df.index.get_level_values('idx'))  == np.array(smap(range(ctable.nrow), lambda x: f'[{x}]')))
    assert np.all(np.array(df.columns.get_level_values('idx')) == np.array(smap(range(ctable.ncol), lambda x: f'[{x}]')))

def test_table_methods_offload():
    table = _create_table()

    fname = 'test_table_memmap'
    ctable = deepcopy(table)
    table.offload(fname)
    assert table == ctable

    table.onload(removefile = True)
    assert table == ctable
    assert not os.path.isfile(fname)

def test_table_methods_portals():
    table = _create_table()
    fname = 'test_table'

    table.savecsv(fname + '.csv')
    ltable = Table.loadcsv(fname + '.csv')
    print(ltable)
    assert ltable == table
    if os.path.isfile(fname + '.csv'): os.remove(fname + '.csv')

    table.savehdf(fname + '.hdf', compression = 9)
    ltable = Table.loadhdf(fname + '.hdf')
    print(ltable)
    assert ltable == table
    if os.path.isfile(fname + '.hdf'): os.remove(fname + '.hdf')

    table.astype(str).savehdf(fname + '.hdf', compression = 9)
    ltable = Table.loadhdf(fname + '.hdf')
    print(ltable)
    assert ltable == table.astype(str)
    if os.path.isfile(fname + '.hdf'): os.remove(fname + '.hdf')

    try: import rpy2
    except ImportError as e: return # Skip if rpy2 is not installed
    table.saverdata(fname + '.rdata', dataobj = 'data', ridxobj = 'row.index', cidxobj = 'col.index')
    ltable = Table.loadrdata(fname + '.rdata', dataobj = 'data', ridxobj = 'row.index', cidxobj = 'col.index')
    print(ltable)
    assert ltable == table
    if os.path.isfile(fname + '.rdata'): os.remove(fname + '.rdata')

