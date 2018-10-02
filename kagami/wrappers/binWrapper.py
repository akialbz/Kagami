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
from kagami.core import NA, optional, isna, hasvalue, listable
from kagami.functional import smap, pmap, tmap, partial, unpack


# for multiprocessing
def _exec(binary, params, stdin, shell, normcodes, mute):
    exelst = [binary] + smap(optional(params, []), lambda x: str(x).strip())
    exestr = join(smap(exelst, lambda x: x.replace(' ', '\ ')), ' ')
    logging.debug('cmd = [%s]' % exestr)

    procs = Popen(exestr if shell else exelst, stdin = PIPE, stdout = PIPE, stderr = PIPE, shell = shell)
    rvals = procs.communicate(input = optional(stdin, None))
    rstrs = smap(rvals, lambda x: '' if x is None else x.strip())
    rcode = procs.returncode

    if rcode in normcodes: logging.log((logging.DEBUG if mute else logging.INFO), join(rstrs, ' | '))
    else: logging.error('execution failed [%d]:\n%s' % (rcode, join(rstrs, ' | ')))
    return rcode, rstrs


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

    def execute(self, params = NA, stdin = NA):
        return _exec(self._bin, params, stdin, self._shell, self._ncode, self._mute)

    def mapexec(self, params = NA, stdin = NA, nthreads = NA, nprocs = NA):
        if hasvalue(params) and hasvalue(stdin) and len(params) != len(stdin): raise RuntimeError('parameters and stdins size not match')
        if isna(params) and isna(stdin): raise RuntimeError('both parameters and stdins are NA')

        if isna(params): params = [NA] * len(stdin)
        if isna(stdin): stdin = [NA] * len(params)

        _map = partial(pmap, nprocs = nprocs) if hasvalue(nprocs) else \
               partial(tmap, nthreads = nthreads) if hasvalue(nthreads) else smap
        return _map([(self._bin, p, s, self._shell, self._ncode, self._mute) for p,s in zip(params, stdin)], unpack(_exec))

