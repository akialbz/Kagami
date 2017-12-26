#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
profile: decorators to profile and debug program

ref: http://coolshell.cn/articles/10822.html

author(s): Albert (aki) Zhou
origin: 08-06-2016

"""


import logging, sys, cProfile, pstats, StringIO, pdb, traceback
from functools import wraps


def profile(func):
    @wraps(func)
    def _wrap(*args, **kwargs):
        prof = cProfile.Profile()
        retval = prof.runcall(func, *args, **kwargs)
        s = StringIO.StringIO()
        pstats.Stats(prof, stream = s).sort_stats('cumulative').print_stats()
        logging.info(s.getvalue() + '\n   return = ' + repr(retval))
    return _wrap

def debug(func):
    @wraps(func)
    def _wrap(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except:
            logging.info('\n---------- DEBUG ----------')
            logging.info(traceback.format_exc())
            pdb.post_mortem(sys.exc_info()[-1])
    return _wrap


