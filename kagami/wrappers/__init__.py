#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
__init__

author(s): Albert
origin: 03-18-2017

"""


from kagami.wrappers.binWrapper import BinaryWrapper
from kagami.wrappers.sqliteWrapper import SQLiteWrapper, createSQLiteWrapper

__all__ = ['BinaryWrapper', 'SQLiteWrapper', 'createSQLiteWrapper']

try:
    from kagami.wrappers.rWrapper import RWrapper, RRuntimeError
    __all__ += ['RWrapper', 'RRuntimeError']
except ImportError: pass

