#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
sqliteWrapper

author(s): Albert (aki) Zhou
origin: 04-12-2017

"""


import logging, sqlite3, os
from kagami.functional import fold
from kagami.filesys import fileTitle


class SQLiteWrapper(object):
    def __init__(self, dbfile, **kwargs):
        self._dbfile = dbfile
        self._dbpams = kwargs
        self._dbconn = None

    # operations
    def connect(self):
        if self._dbconn is not None:
            logging.debug('database [%s] already connected, ignore' % fileTitle(self._dbfile))
        else:
            logging.debug('%s SQLite database [%s]' %
                ('connecting' if os.path.isfile(self._dbfile) else 'creating', fileTitle(self._dbfile)))
            self._dbconn = sqlite3.connect(self._dbfile, **self._dbpams)
        return self

    def commit(self):
        if self._dbconn is None: raise IOError('database not connected')
        self._dbconn.commit()

    def close(self, commit = True):
        if self._dbconn is None:
            logging.debug('connection to database [%s] already closed, ignore' % fileTitle(self._dbfile))
        else:
            logging.debug('closing connection to SQLite database [%s]' % fileTitle(self._dbfile))
            if commit: self._dbconn.commit()
            self._dbconn.close()
            self._dbconn = None
        return self

    def execute(self, query):
        if self._dbconn is None: raise IOError('database not connected')
        logging.debug('exec = [%s]' % query)
        try:
            self._dbconn.execute(query)
        except Exception, e:
            logging.warning('sqlite query failed: ' + str(e))

    def query(self, query):
        if self._dbconn is None: raise IOError('database not connected')
        logging.debug('query = [%s]' % query)
        try:
            res = self._dbconn.execute(query).fetchall()
        except Exception, e:
            logging.warning('sqlite query failed: ' + str(e))
            res = []
        return res

    # routines
    def tableExists(self, tableName):
        res = self.query("SELECT name FROM sqlite_master WHERE type='table' AND name='%s';" % tableName)
        return len(res) > 0

    def listTables(self):
        res = self.query("SELECT name FROM sqlite_master WHERE type='table';")
        return fold(res, lambda x,y: x+y, ())

    def listColumns(self, tableName):
        return self.query("PRAGMA table_info('%s')" % tableName)

    def listColNames(self, tableName):
        cols = self.listColumns(tableName)
        return zip(*cols)[1] if len(cols) > 0 else ()

    def toList(self, tableName):
        return self.query("SELECT * FROM '%s';" % tableName)


# with ... as statement
class createSQLiteWrapper:
    def __init__(self, dbfile, **kwargs):
        self._dbfile = dbfile
        self._params = kwargs
        self._db = None

    def __enter__(self):
        self._db = SQLiteWrapper(self._dbfile, **self._params).connect()
        return self._db

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._db.close()

