#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
csvPortal: portals to access csv / tsv files

author(s): Albert (aki) Zhou
origin: 06-28-2014

"""


import logging, os, csv
from ast import literal_eval
from ..prelim import NA, hasvalue
from ..functional import pipe, do
from ..fileSys import checkInputFile, checkOutputFile


def loadCSV(fname, headRows = NA, autoEval = False, **kwargs):
    checkInputFile(fname)

    with open(fname, 'rU') as f:
        hd = [next(f).rstrip('\n') for _ in range(headRows)] if hasvalue(headRows) else None
        dm = list(csv.reader(f, **kwargs))

    def _eval(x):
        try: return literal_eval(x)
        except (ValueError, SyntaxError): str(x)
    if autoEval: dm = pipe(dm | do(lambda ln: map(_eval, ln)))

    return dm if hd is None else (hd, dm)

def saveCSV(dm, fname, heads = NA, **kwargs):
    checkOutputFile(fname)

    with open(fname, 'w') as f:
        if hasvalue(heads): f.writelines(pipe(heads | do(str) | do(lambda x: x + ('' if x.endswith('\n') else '\n'))))
        csv.writer(f, **kwargs).writerows(pipe(list(dm) | do(lambda ln: map(str, ln))))

    return os.path.isfile(fname)

def loadTSV(fname, headRows = NA, autoEval = False, **kwargs):
    if kwargs.has_key('delimiter'): logging.warning('setting delimiter for TSV portal')
    kwargs.update(delimiter = '\t')
    return loadCSV(fname, headRows, autoEval, **kwargs)

def saveTSV(dm, fname, heads = NA, **kwargs):
    if kwargs.has_key('delimiter'): logging.warning('setting delimiter for TSV portal')
    kwargs.update(delimiter = '\t')
    return saveCSV(dm, fname, heads, **kwargs)

