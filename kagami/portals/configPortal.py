#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
configPortal

author(s): Albert (aki) Zhou
origin: 06-03-2014

"""


import logging
from ConfigParser import ConfigParser
from collections import OrderedDict
from kagami.core import na, autoeval, checkInputFile


class _NoConvConfigParser(ConfigParser):
    def optionxform(self, optionstr): return optionstr


def load(cfgFile, autoEval = True, dictType = OrderedDict, emptyAsMissing = False):
    logging.debug('loading configs from [%s]' % cfgFile)
    checkInputFile(cfgFile)

    cfg = _NoConvConfigParser()
    cfg.read(cfgFile)

    def _eval(x):
        if not autoEval: return x
        val = autoeval(x)
        if x not in ("''", '""') and val == '' and emptyAsMissing: val = na
        return val

    _items = lambda x: dictType([(k, _eval(v)) for k,v in cfg.items(x)])
    return dictType([(s, _items(s)) for s in cfg.sections()])

