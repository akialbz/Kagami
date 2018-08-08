#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
gffPortal

author(s): Albert (aki) Zhou
origin: 01-26-2018

"""


import logging
from string import join
from collections import namedtuple
from operator import itemgetter
from kagami.core.prelim import NA, optional
from kagami.core.functional import pipe, do, pick, drop
from kagami.core.portals.textPortal import loadTextLines, saveTextLines


_GFFCols = ('seqName', 'source', 'feature', 'start', 'end', 'score', 'strand', 'frame', 'attributes')
GFFFeature = namedtuple('GFFFeature', _GFFCols)


def _checkFeature(seqn, src, feat, st, ed, scor, strd, fram, attr):
    if not st.isdigit(): logging.warning('invalid start position [%s]' % st); return False
    if not ed.isdigit(): logging.warning('invalid end position [%s]' % ed); return False
    if strd not in ('+', '-', '.'): logging.warning('invalid strand [%s]' % strd); return False
    if fram not in ('0', '1', '2', '.'): logging.warning('invalid frame [%s]' % fram); return False
    invattr = pipe(attr.split(';') | pick(lambda x: len(x.split('=')) != 2))
    if len(invattr) > 0: logging.warning('[%d] invalid attributes found in [%s]' % (len(invattr), attr)); return False
    return True

def loadGFF(fpath, check = True, raiseError = True):
    _parseAttrs = lambda astr: pipe(astr.split(';') | do(lambda x: x.split('=',1)), dict)

    def _parse(ln):
        cols = ln.split('\t')
        if len(cols) != 9: raise ValueError('feature line [%s] contains incorrect number of columns' % ln)
        passchk = True if not check else _checkFeature(*cols)
        if not passchk and raiseError: raise ValueError('error(s) found in the GFF checking')
        return GFFFeature(*(cols[:-1] + [_parseAttrs(cols[-1])]))

    rlns = loadTextLines(fpath)
    return pipe(rlns | drop(lambda x: x == '.' or x.startswith('#')) | do(_parse))

def saveGFF(gffFeats, fpath, check = True, raiseError = True, heads = NA):
    _packAttrs = lambda adct: pipe(adct.items() | do(lambda x: join(map(str,x), '=')), lambda x: join(x, ';'))

    def _pack(ft):
        cols = itemgetter(*_GFFCols)(ft)
        cols = map(str, cols[:-1]) + [_packAttrs(cols[-1])]
        passchk = True if not check else _checkFeature(*cols)
        if not passchk and raiseError: raise ValueError('error(s) found in the GFF checking')
        return join(cols, '\t')

    return saveTextLines(list(optional(heads, [])) + pipe(gffFeats | do(_pack)), fpath)
