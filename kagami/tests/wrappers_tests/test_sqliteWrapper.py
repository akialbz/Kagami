#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
test_sqliteWrapper

author(s): Albert (aki) Zhou
added: 11-22-2018

"""


from pathlib import Path
from kagami.comm import *
from kagami.wrappers import SQLiteWrapper, openSQLiteWrapper


def test_creation_context():
    fn = Path('test_sqlite_wrapper.db')
    with openSQLiteWrapper(fn) as db:
        assert fn.is_file()
        assert db.connected
    assert not db.connected
    fn.unlink()

def test_basic_operations():
    fn = Path('test_sqlite_wrapper.db')
    db = SQLiteWrapper(fn).connect()
    assert fn.is_file()
    assert db.connected

    db.close()
    assert not db.connected
    fn.unlink()

def test_table_operations():
    fn = Path('test_sqlite_wrapper.db')

    with openSQLiteWrapper(fn) as db:
        tabn = 'new table'
        assert not db.tableExists(tabn)

        db.createTable(tabn, [('idx', 'INT', 'PRIMARY KEY', 'UNIQUE', 'NOT NULL'), ('name', 'TEXT')]).commit()
        assert db.tableExists(tabn)
        assert tabn in db.listTables()

        db.dropTable(tabn).commit()
        assert not db.tableExists(tabn)

    fn.unlink()

def test_column_operations():
    fn = Path('test_sqlite_wrapper.db')

    with openSQLiteWrapper(fn) as db:
        tabn = 'new table'
        db.createTable(tabn, [('idx', 'INT', 'PRIMARY KEY', 'UNIQUE', 'NOT NULL'), ('name', 'TEXT')]).commit()
        assert db.columnExists(tabn, 'name')

        coln = 'new col'
        assert not db.columnExists(tabn, coln)

        db.addColumn(tabn, coln, ('TEXT',)).commit()
        assert db.columnExists(tabn, coln)
        assert coln in db.listColNames(tabn)
        assert coln in lzip(*db.listColumns(tabn))[1]

        dm = [(1, 'a', 'val 1'), (2, 'b', 'val 2')]
        for d in dm: db.execute(f"INSERT INTO {tabn} VALUES (%d,'%s','%s')" % d)
        assert checkall(zip(db.tolist(tabn), dm), unpack(lambda x,y: x == y))

    fn.unlink()

