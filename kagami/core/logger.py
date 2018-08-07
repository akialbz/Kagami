#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
logConfig

author(s): Albert (aki) Zhou
origin: 12-11-2014

"""


import logging, sys
from kagami.core.prelim import NA, hasvalue, optional


# default formats
LEVEL_FORMATS = {
    logging.DEBUG:    'D> %(message)s',
    logging.INFO:     '   %(message)s',
    logging.WARN:     '\n ?? [ WARNING ] ?? %(message)s \n',
    logging.ERROR:    '\n !!! [ ERROR ] !!! %(message)s \n',
    logging.CRITICAL: '\n !!! [ FATAL ] !!! %(message)s \n',
}
LOGFILE_FORMAT = '%(asctime)-15s : [%(levelname)s] >> %(message)s'
EXCEPTION_FORMAT = '%(class)s: %(message)s'


# handlers
class _LevelFormatter(logging.Formatter):
    def __init__(self, *args, **kwargs):
        self._fmtdict = LEVEL_FORMATS
        logging.Formatter.__init__(self, *args, **kwargs)

    def format(self, record):
        if not self._fmtdict.has_key(record.levelno):
            raise KeyError('unknown logging level [%s]' % str(record.levelno))
        self._fmt = self._fmtdict[record.levelno]
        return logging.Formatter.format(self, record)

class _QuitHandler(logging.Handler):
    def emit(self, record):
        logging.shutdown()
        sys.exit(1)


# config interface
def configLogger(level = logging.INFO, fatalLevel = logging.FATAL,
                  consoleFmt = NA, logFile = NA, logMode = 'w', logFmt = NA, exceptionFmt = NA):
    logger = logging.getLogger()
    logger.handlers = [] # remove existing handlers
    logger.setLevel(level)

    # log to console
    pfmt = optional(consoleFmt, _LevelFormatter())
    if not isinstance(pfmt, logging.Formatter): raise TypeError('print formatter is not a Formatter object')
    chdl = logging.StreamHandler()
    chdl.setFormatter(pfmt)
    logger.addHandler(chdl)

    # log to file
    if hasvalue(logFile):
        lfmt = optional(logFmt, logging.Formatter(LOGFILE_FORMAT))
        if not isinstance(lfmt, logging.Formatter): raise TypeError('log file formatter is not a Formatter object')
        fhdl = logging.FileHandler(logFile, mode = logMode)
        fhdl.setFormatter(lfmt)
        logger.addHandler(fhdl)

    # handle exception / assertion
    efmt = optional(exceptionFmt, EXCEPTION_FORMAT)
    if not isinstance(efmt, str): raise TypeError('exception format is not a string object')
    def _excepthook(*args):
        logger.fatal(
            efmt % {'class': args[1].__class__.__name__, 'message': args[1].message},
            exc_info = False if level > logging.DEBUG else args
        )
    sys.excepthook = _excepthook

    # quit on fatal
    logger.addHandler(_QuitHandler(level = fatalLevel))

    return logger # to add extra handlers

