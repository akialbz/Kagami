#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
tablePortal

author(s): Albert (aki) Zhou
origin: 06-28-2014

"""


import logging, os, csv
from kagami.core import na, available, autoeval, smap, pickmap, checkInputFile, checkOutputFile


# csv portals
def loadcsv(tabFile, headRows = na, autoEval = False, wrap = na, mode = 'rU', **kwargs):
    logging.debug('loading table from [%s]' % tabFile)
    checkInputFile(tabFile)

    with open(tabFile, mode) as f:
        hd = [next(f).rstrip('\n') for _ in range(headRows)] if available(headRows) else None
        tb = list(csv.reader(f, **kwargs))
    if autoEval: tb = smap(tb, lambda x: smap(x, autoeval))

    if available(wrap): tb = wrap(tb)
    return (hd, tb) if available(headRows) else tb

def savecsv(table, tabFile, heads = na, mode = 'w', **kwargs):
    logging.debug('saving table to [%s]' % tabFile)
    checkOutputFile(tabFile)

    with open(tabFile, mode) as f:
        if available(heads): f.writelines(pickmap(smap(heads, str), lambda x: not x.endswith('\n'), lambda x: x + '\n'))
        csv.writer(f, **kwargs).writerows(smap(table, lambda x: smap(x,str)))

    return os.path.isfile(tabFile)


# general / tsv portals
def load(tabFile, delimiter = '\t', headRows = na, autoEval = False, wrap = na, mode = 'rU', **kwargs):
    return loadcsv(tabFile, headRows = headRows, autoEval = autoEval, wrap = wrap, mode = mode, delimiter = delimiter, **kwargs)

def save(table, tabFile, delimiter = '\t', heads = na, mode = 'w', **kwargs):
    return savecsv(table, tabFile, heads =  heads, mode = mode, delimiter = delimiter, **kwargs)

