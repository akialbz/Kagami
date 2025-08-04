#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
sqliteWrapper

author(s): Albert (aki) Zhou
added: 04-12-2017

"""


from __future__ import annotations

import logging, sqlite3
from pathlib import Path
from typing import List, Tuple, Iterable, Optional, Union, Any
from kagami.comm import available, missing, optional, smap, lzip, collapse, paste, fileTitle


__all__ = ['SQLiteWrapper', 'openSQLiteWrapper']


class SQLiteWrapper:
    def __init__(self, dbfile: Union[str, Path], **kwargs: Any):
        self._dbfile = Path(dbfile)
        self._dbpams = kwargs
        self._dbconn = None

    # properties
    @property
    def connected(self) -> bool:
        return available(self._dbconn)

    # operations
    def connect(self) -> SQLiteWrapper:
        if available(self._dbconn):
            logging.warning('database [%s] already connected, ignore', fileTitle(self._dbfile))
        else:
            self._dbconn = sqlite3.connect(self._dbfile, **self._dbpams)
        return self

    def commit(self) -> SQLiteWrapper:
        if missing(self._dbconn): raise IOError('database not connected')
        self._dbconn.commit()
        return self

    def close(self, commit: bool = True) -> SQLiteWrapper:
        if missing(self._dbconn):
            logging.warning('connection to database [%s] already closed, ignore', fileTitle(self._dbfile))
        else:
            if commit: self._dbconn.commit()
            self._dbconn.close()
            self._dbconn = None
        return self

    def execute(self, query: str) -> SQLiteWrapper:
        if missing(self._dbconn): raise IOError('database not connected')
        try:
            self._dbconn.execute(query)
        except Exception as e:
            logging.warning('sqlite execution failed: %s', str(e))
        return self

    def query(self, query: str) -> List:
        if self._dbconn is None: raise IOError('database not connected')
        try:
            res = self._dbconn.execute(query).fetchall()
        except Exception as e:
            logging.warning('sqlite query failed: %s', str(e))
            res = []
        return res

    # table routines
    def createTable(self, tableName: str, columns: Iterable[Iterable[str]] = ()) -> SQLiteWrapper:
        tcols = paste(smap(columns, lambda x: paste(x, sep = ' ')), sep = ', ')
        self.execute(f"CREATE TABLE '{tableName}'({tcols})")
        return self

    def dropTable(self, tableName: str) -> SQLiteWrapper:
        self.execute(f"DROP TABLE IF EXISTS '{tableName}'")
        return self

    def tableExists(self, tableName: str) -> bool:
        res = self.query(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{tableName}'")
        return len(res) > 0

    def listTables(self) -> Tuple:
        res = self.query("SELECT name FROM sqlite_master WHERE type='table'")
        return collapse(res, ())

    # column routines
    def addColumn(self, tableName: str, colName: str, types: Optional[Iterable[str]] = None) -> SQLiteWrapper:
        tstr = paste(optional(types, []), sep = ' ')
        self.execute(f"ALTER TABLE '{tableName}' ADD COLUMN '{colName}' {tstr}" )
        return self

    def columnExists(self, tableName: str, colName: str) -> bool:
        return colName in self.listColNames(tableName)

    def listColumns(self, tableName: str) -> List:
        return self.query(f"PRAGMA table_info('{tableName}')")

    def listColNames(self, tableName: str) -> List:
        cols = self.listColumns(tableName)
        return lzip(*cols)[1] if len(cols) > 0 else []

    # export
    def tolist(self, tableName: str) -> List:
        return self.query(f"SELECT * FROM '{tableName}'")


# with ... as statement
class openSQLiteWrapper:
    def __init__(self, dbfile: Union[str, Path], **kwargs: Any):
        self._dbfile = dbfile
        self._params = kwargs
        self._db = None

    def __enter__(self):
        self._db = SQLiteWrapper(self._dbfile, **self._params).connect()
        return self._db

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._db.close()

