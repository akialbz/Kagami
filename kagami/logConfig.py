#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
logConfig: config logging system

author(s): Albert (aki) Zhou
origin: 12-11-2014

"""


import logging, sys
from prelim import NA, hasvalue, optional


class LevelFormatter(logging.Formatter):
    def __init__(self, fmtDict = NA, *args, **kwargs):
        self._fmtdict = optional(fmtDict, {
            logging.DEBUG: ' D> %(message)s',
            logging.INFO:  '    %(message)s',
            logging.WARN:  '\n ?? WARNING: %(message)s \n',
            logging.ERROR: '\n !! ERROR: %(message)s \n',
        })
        logging.Formatter.__init__(self, *args, **kwargs)

    def format(self, record):
        if not self._fmtdict.has_key(record.levelno):
            raise KeyError('unknown logging level [%s]' % str(record.levelno))
        self._fmt = self._fmtdict[record.levelno]
        return logging.Formatter.format(self, record)


def configLogging(level = logging.INFO, printFmt = NA, logFile = NA, logMode = 'w', logFmt = NA, exceptionFmt = NA):
    logger = logging.getLogger()
    logger.handlers = [] # remove existing handlers
    logger.setLevel(level)

    # log to terminal
    if hasvalue(printFmt) and not isinstance(printFmt, logging.Formatter):
        raise TypeError('print formatter is not a Formatter object')
    pfmt = optional(printFmt, LevelFormatter())
    chdl = logging.StreamHandler()
    chdl.setFormatter(pfmt)
    logger.addHandler(chdl)

    # log to file
    if hasvalue(logFile):
        if hasvalue(logFmt) and not isinstance(logFmt, logging.Formatter):
            raise TypeError('log file formatter is not a Formatter object')
        lfmt = optional(logFmt, logging.Formatter('%(asctime)-15s : [%(levelname)s] >> %(message)s'))
        fhdl = logging.FileHandler(logFile, mode = logMode)
        fhdl.setFormatter(lfmt)
        logger.addHandler(fhdl)

    # handle exception / assertion
    if hasvalue(exceptionFmt) and not isinstance(exceptionFmt, str):
        raise TypeError('exception format is not a string object')
    def _excepthook(*args):
        logging.getLogger().error(
            optional(exceptionFmt, '%(class)s: %(message)s') %
            {'class': args[1].__class__.__name__, 'message': args[1].message},
            exc_info = False if level > logging.DEBUG else args
        )
    sys.excepthook = _excepthook

    return logger # to add extra handlers

