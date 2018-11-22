#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
test_sqliteWrapper

author(s): Albert (aki) Zhou
origin: 11-22-2018

"""


import os
from kagami.core import *
from kagami.wrappers import SQLiteWrapper, openSQLiteWrapper


def test_creation_context():
    fn = 'test_sqlite_wrapper.db'
    with openSQLiteWrapper(fn) as db:
        assert os.path.isfile(fn)
        assert db.connected
    assert not db.connected
    os.remove(fn)

def test_basic_operations():
    fn = 'test_sqlite_wrapper.db'
    db = SQLiteWrapper(fn).connect()
    assert os.path.isfile(fn)
    assert db.connected

    db.close()
    assert not db.connected
    os.remove(fn)

def test_table_operations():
    fn = 'test_sqlite_wrapper.db'

    with openSQLiteWrapper(fn) as db:
        tabn = 'new table'
        assert not db.tableExists(tabn)

        db.createTable(tabn, [('idx', 'INT', 'PRIMARY KEY', 'UNIQUE', 'NOT NULL'), ('name', 'TEXT')]).commit()
        assert db.tableExists(tabn)
        assert tabn in db.listTables()

        db.dropTable(tabn).commit()
        assert not db.tableExists(tabn)

    os.remove(fn)

def test_column_operations():
    fn = 'test_sqlite_wrapper.db'

    with openSQLiteWrapper(fn) as db:
        tabn = 'new table'
        db.createTable(tabn, [('idx', 'INT', 'PRIMARY KEY', 'UNIQUE', 'NOT NULL'), ('name', 'TEXT')]).commit()
        assert db.columnExists(tabn, 'name')

        coln = 'new col'
        assert not db.columnExists(tabn, coln)

        db.addColumn(tabn, coln, ('TEXT',)).commit()
        assert db.columnExists(tabn, coln)
        assert coln in db.listColNames(tabn)
        assert coln in zip(*db.listColumns(tabn))[1]

        dm = [(1, 'a', 'val 1'), (2, 'b', 'val 2')]
        for d in dm: db.execute("INSERT INTO %s VALUES (%d,'%s','%s')" % ((tabn,) + d))
        assert checkall(zip(db.toList(tabn), dm), unpack(lambda x,y: x == y))

    os.remove(fn)

