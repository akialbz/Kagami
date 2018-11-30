#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
binWrapper

author(s): Albert (aki) Zhou
origin: 01-25-2016

"""


import logging
from string import join
from subprocess import Popen, PIPE
from distutils.spawn import find_executable
from kagami.core import na, isnull, optional, missing, available, listable, smap, pmap, tmap, partial


# for multiprocessing
def _exec(binary, params, stdin, shell, normcodes, mute):
    exelst = [binary] + smap([] if isnull(params) else params, lambda x: str(x).strip())
    exestr = join(smap(exelst, lambda x: x.replace(' ', '\ ')), ' ')
    logging.debug('running binary cmd = [%s]' % exestr)

    procs = Popen(exestr if shell else exelst, stdin = PIPE, stdout = PIPE, stderr = PIPE, shell = shell)
    rvals = procs.communicate(input = optional(stdin, None))
    rstrs = smap(rvals, lambda x: '' if x is None else x.strip())
    rcode = procs.returncode

    if rcode in normcodes: logging.log((logging.DEBUG if mute else logging.INFO), join(rstrs, ' | '))
    else: logging.error('execution failed [%d]:\n%s' % (rcode, join(rstrs, ' | ')))
    return rcode, rstrs

def _mp_exec(params):
    return _exec(*params)

class BinaryWrapper(object):
    def __init__(self, binName, shell = False, normalExit = 0, mute = False):
        self._bin = self.which(binName)
        if self._bin is None: raise RuntimeError('binary executable [%s] not reachable' % binName)
        self._shell = shell
        self._ncode = normalExit if listable(normalExit) else (normalExit,)
        self._mute = mute

    # methods
    @staticmethod
    def which(binName):
        if binName.startswith('./'): binName = binName[2:]
        return find_executable(binName)

    @staticmethod
    def reachable(binName):
        return BinaryWrapper.which(binName) is not None

    def execute(self, params = na, stdin = na):
        return _exec(self._bin, params, stdin, self._shell, self._ncode, self._mute)

    def mapexec(self, params = na, stdin = na, nthreads = na, nprocs = na):
        if available(params) and available(stdin) and len(params) != len(stdin): raise RuntimeError('parameters and stdins size not match')
        if missing(params) and missing(stdin): raise RuntimeError('both parameters and stdins are missing')

        if missing(params): params = [na] * len(stdin)
        if missing(stdin): stdin = [na] * len(params)

        _map = partial(pmap, nprocs = nprocs) if available(nprocs) else \
               partial(tmap, nthreads = nthreads) if available(nthreads) else smap
        return _map([(self._bin, p, s, self._shell, self._ncode, self._mute) for p,s in zip(params, stdin)], _mp_exec)

