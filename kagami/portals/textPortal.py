#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
textPortal: portals to access plain text files

author(s): Albert (aki) Zhou
origin: 06-28-2014

"""


from string import strip
from types import StringType, UnicodeType
from ..prelim import checkany
from ..functional import pipe, do, drop, skip
from ..fileSys import checkInputFile, checkOutputFile


# raw text string
def loadText(fpath, striping = True):
    checkInputFile(fpath)
    with open(fpath, 'r') as f: txt = f.read()
    return strip(txt) if striping else txt

def saveText(txt, fpath):
    if not isinstance(txt, (StringType, UnicodeType)): raise TypeError('export object is not a string')
    checkOutputFile(fpath)
    with open(fpath, 'w') as f: f.write(txt)

# raw text lines
def loadTextLines(fpath, striping = True, removeBlanks = True):
    checkInputFile(fpath)
    with open(fpath, 'rU') as f: tlines = f.readlines()
    return pipe(tlines | (do(strip) if striping else do(lambda x: x.rstrip('\n')))
                       | (drop(lambda x: strip(x) == '') if removeBlanks else skip))

def saveTextLines(tlines, fpath, autoReturn = True):
    if checkany(tlines, lambda x: not isinstance(x, (StringType, UnicodeType))):
        raise TypeError('export object is not a string list')
    checkOutputFile(fpath)
    with open(fpath, 'w') as ofile:
        ofile.writelines(pipe(tlines | (do(lambda x: x + ('' if x.endswith('\n') else '\n')) if autoReturn else skip)))
