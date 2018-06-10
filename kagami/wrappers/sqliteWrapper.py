#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
sqliteWrapper: wrapper for SQLite3 database

author(s): Albert (aki) Zhou
origin: 04-12-2017

"""


import logging, sqlite3, os
from ..fileSys import fileTitle


class SQLiteWrapper(object):
    def __init__(self, dbfile, **kwargs):
        self._dbfile = dbfile
        self._dbpams = kwargs
        self._dbconn = None

    # using with ... as
    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    # methods
    def connect(self):
        if self._dbconn is not None:
            logging.warning('database [%s] already connected, ignore' % fileTitle(self._dbfile))
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
            logging.warning('connection to database [%s] already closed, ignore' % fileTitle(self._dbfile))
        else:
            logging.debug('closing connection to SQLite database [%s]' % fileTitle(self._dbfile))
            if commit: self._dbconn.commit()
            self._dbconn.close()
            self._dbconn = None
        return self

    def execute(self, query):
        if self._dbconn is None: raise IOError('database not connected')
        logging.debug('exec command = [%s]' % query)
        try: self._dbconn.execute(query)
        except Exception, e: logging.warning('sqlite query failed: ' + str(e))

    def query(self, query):
        if self._dbconn is None: raise IOError('database not connected')
        logging.debug('query command = [%s]' % query)
        try:
            res = self._dbconn.execute(query).fetchall()
        except Exception, e:
            logging.warning('sqlite query failed: ' + str(e))
            res = []
        return res

    def tableExists(self, tableName):
        res = self.query("SELECT name FROM sqlite_master WHERE type='table' AND name='%s';" % tableName)
        return len(res) > 0

    def listTables(self):
        res = self.query("SELECT name FROM sqlite_master WHERE type='table';")
        return reduce(lambda x,y: x+y, res, ())

    def listColumns(self, tableName):
        return self.query("PRAGMA table_info('%s')" % tableName)

    def listColNames(self, tableName):
        cols = self.listColumns(tableName)
        return zip(*cols)[1] if len(cols) > 0 else ()

    def toList(self, tableName):
        return self.query("SELECT * FROM '%s';" % tableName)

