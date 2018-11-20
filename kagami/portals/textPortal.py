#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
textPortal

author(s): Albert (aki) Zhou
origin: 06-28-2014

"""


import logging, os
from string import strip
from kagami.core import smap, drop, pickmap, checkInputFile, checkOutputFile


# raw text string
def load(txtFile, striping = True):
    logging.debug('loading text from [%s]' % txtFile)
    checkInputFile(txtFile)
    with open(txtFile, 'r') as f: txt = f.read()
    return strip(txt) if striping else txt

def save(txt, txtFile):
    logging.debug('saving text to [%s]' % txtFile)
    checkOutputFile(txtFile)
    with open(txtFile, 'w') as f: f.write(str(txt))
    return os.path.isfile(txtFile)

# raw text lines
def loadlns(txtFile, striping = True, removeBlanks = True):
    logging.debug('loading textlines from [%s]' % txtFile)
    checkInputFile(txtFile)

    with open(txtFile, 'rU') as f: tlines = f.readlines()
    tlines = smap(tlines, lambda x: x.rstrip('\n'))
    if striping: tlines = smap(tlines, strip)
    if removeBlanks: tlines = drop(tlines, lambda x: x.strip() == '')

    return tlines

def savelns(tlines, txtFile, autoReturn = True):
    logging.debug('saving textlines to [%s]' % txtFile)
    checkOutputFile(txtFile)

    tlines = smap(tlines, str)
    if autoReturn: tlines = pickmap(tlines, lambda x: not x.endswith('\n'), lambda x: x + '\n')
    with open(txtFile, 'w') as ofile: ofile.writelines(tlines)

    return os.path.isfile(txtFile)
