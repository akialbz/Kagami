#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
configPortal: portal to access config files

author(s): Albert Zhou
origin: 06-03-2014

"""


import logging
from ConfigParser import ConfigParser
from ast import literal_eval
from collections import OrderedDict
from ..prelim import NA
from ..functional import pipe, do, unpack
from ..fileSys import checkInputFile


class _NoConvConfigParser(ConfigParser):
    def optionxform(self, optionstr): return optionstr

def loadConfig(cfgFile, autoEval = True, dictType = OrderedDict):
    logging.debug('loading config file [%s]' % cfgFile)
    checkInputFile(cfgFile)

    cfg = _NoConvConfigParser()
    cfg.read(cfgFile)

    def _eval(x):
        try:
            return literal_eval(x)
        except (ValueError, SyntaxError):
            val = str(x).strip()
            return NA if val == 'NA' else val # make NA a valid value in config
    _packsect = lambda s: (s, pipe(cfg.items(s) | do(unpack(lambda k,v: (k, _eval(v) if autoEval else v))), dictType))
    return pipe(cfg.sections() | do(_packsect), dictType)
