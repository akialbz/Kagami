#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
configPortal

author(s): Albert (aki) Zhou
origin: 06-03-2014

"""


import logging
from ConfigParser import ConfigParser
from ast import literal_eval
from collections import OrderedDict
from kagami.prelim import NA
from kagami.filesys import checkInputFile


class _NoConvConfigParser(ConfigParser):
    def optionxform(self, optionstr): return optionstr

def load(cfgFile, autoEval = True, dictType = OrderedDict, emptyAsNA = True):
    logging.debug('loading configs from [%s]' % cfgFile)
    checkInputFile(cfgFile)

    cfg = _NoConvConfigParser()
    cfg.read(cfgFile)

    def _eval(x):
        if not autoEval: return x
        try:
            return literal_eval(x)
        except (ValueError, SyntaxError):
            val = str(x).strip()
            if val == 'NA': val = NA # make NA a valid value in config
            if val == '' and emptyAsNA: val = NA
            return val
    return dictType([(sect, dictType([(k, _eval(v)) for k,v in cfg.items(sect)])) for sect in cfg.sections()])

