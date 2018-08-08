#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
tablePortal

author(s): Albert (aki) Zhou
origin: 06-28-2014

"""


import logging, os, csv
from ast import literal_eval
from kagami.core.prelim import NA, hasvalue
from kagami.core.functional import smap, pickmap
from kagami.core.filesys import checkInputFile, checkOutputFile


def loadCSV(tabFile, headRows = NA, autoEval = False, **kwargs):
    logging.debug('loading table from [%s]' % tabFile)
    checkInputFile(tabFile)

    with open(tabFile, 'rU') as f:
        hd = [next(f).rstrip('\n') for _ in range(headRows)] if hasvalue(headRows) else None
        tb = list(csv.reader(f, **kwargs))

    def _eval(x):
        try: return literal_eval(x)
        except (ValueError, SyntaxError): str(x)
    if autoEval: tb = smap(tb, lambda x: smap(x, _eval))

    return (tb, hd) if hasvalue(headRows) else tb

def saveCSV(table, tabFile, heads = NA, **kwargs):
    logging.debug('saving table to [%s]' % tabFile)
    checkOutputFile(tabFile)

    with open(tabFile, 'w') as f:
        if hasvalue(heads): f.writelines(pickmap(smap(heads, str), lambda x: not x.endswith('\n'), lambda x: x + '\n'))
        csv.writer(f, **kwargs).writerows(smap(table, lambda x: smap(x,str)))

    return os.path.isfile(tabFile)

def load(tabFile, delimiter = '\t', headRows = NA, autoEval = False, **kwargs):
    return loadCSV(tabFile, headRows, autoEval, delimiter = delimiter, **kwargs)

def save(table, tabFile, delimiter = '\t', heads = NA, **kwargs):
    return saveCSV(table, tabFile, heads, delimiter = delimiter, **kwargs)

