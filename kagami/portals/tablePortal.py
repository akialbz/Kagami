#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
tablePortal

author(s): Albert (aki) Zhou
origin: 06-28-2014

"""


import logging, os, csv
from kagami.core import NA, hasvalue, autoeval, smap, pickmap, checkInputFile, checkOutputFile


def loadcsv(tabFile, headRows = NA, autoEval = False, wrap = NA, **kwargs):
    logging.debug('loading table from [%s]' % tabFile)
    checkInputFile(tabFile)

    with open(tabFile, 'rU') as f:
        hd = [next(f).rstrip('\n') for _ in range(headRows)] if hasvalue(headRows) else None
        tb = list(csv.reader(f, **kwargs))
    if autoEval: tb = smap(tb, lambda x: smap(x, autoeval))

    if hasvalue(wrap): tb = wrap(tb)
    return (hd, tb) if hasvalue(headRows) else tb

def savecsv(table, tabFile, heads = NA, **kwargs):
    logging.debug('saving table to [%s]' % tabFile)
    checkOutputFile(tabFile)

    with open(tabFile, 'w') as f:
        if hasvalue(heads): f.writelines(pickmap(smap(heads, str), lambda x: not x.endswith('\n'), lambda x: x + '\n'))
        csv.writer(f, **kwargs).writerows(smap(table, lambda x: smap(x,str)))

    return os.path.isfile(tabFile)

def load(tabFile, delimiter = '\t', headRows = NA, autoEval = False, wrap = NA, **kwargs):
    return loadcsv(tabFile, headRows = headRows, autoEval = autoEval, wrap = wrap, delimiter = delimiter, **kwargs)

def save(table, tabFile, delimiter = '\t', heads = NA, **kwargs):
    return savecsv(table, tabFile, heads =  heads, delimiter = delimiter, **kwargs)

