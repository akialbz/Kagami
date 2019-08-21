#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
binWrapper

author(s): Albert (aki) Zhou
origin: 01-25-2016

"""


import logging
from pathlib import Path
from typing import Tuple, List, Iterable, Sequence, Optional, Union
from subprocess import Popen, PIPE
from distutils.spawn import find_executable
from kagami.common import optional, missing, available, listable, smap, pmap, tmap, partial, paste


__all__ = ['BinaryWrapper']


# for multiprocessing
class BinaryWrapper:
    def __init__(self, binary: Union[str, Path], shell: bool = False, normcodes: Union[int, Iterable[int]] = 0, mute: bool = False):
        self._bin = self.which(binary)
        if missing(self._bin): raise RuntimeError(f'binary executable [{binary}] not reachable')
        self._shell = shell
        self._ncode = (normcodes,) if isinstance(normcodes, int) else list(normcodes) if not listable(normcodes) else normcodes
        self._mute = mute

    # privates
    def _exec(self, pms):
        params, stdin = pms # for multiproc

        exlst = [self._bin] + ([] if missing(params) else smap(params, lambda x: str(x).strip()))
        if self._shell: exlst = paste(smap(exlst, lambda x: x.replace(' ', r'\ ')), sep = ' ')

        procs = Popen(exlst, stdin = PIPE, stdout = PIPE, stderr = PIPE, shell = self._shell)
        rvals = procs.communicate(input = stdin)
        rstrs = smap(rvals, lambda x: '' if x is None else x.strip())
        rcode = procs.returncode

        prstr = paste(rstrs, ' | ')
        if rcode in self._ncode:
            logging.log((logging.DEBUG if self._mute else logging.INFO), prstr)
        else:
            raise RuntimeError(f'execution failed [{rcode}]:\n{prstr}')
        return rcode, rstrs

    # methods
    @staticmethod
    def which(binary: Union[str, Path]) -> Union[str, None]:
        return find_executable(binary)

    @staticmethod
    def reachable(binary: Union[str, Path]) -> bool:
        return available(BinaryWrapper.which(binary))

    def execute(self, params: Optional[Sequence] = None, stdin: Optional[Union[bytes, str]] = None) -> Tuple[int, List[str]]:
        return self._exec([params, stdin])

    def mapexec(self, params: Optional[Iterable[Sequence]] = None, stdin: Optional[Iterable[Union[bytes, str]]] = None,
                nthreads: Optional[int] = None, nprocs: Optional[int] = None) -> List[Tuple[int, List[str]]]:
        if available(params) and not listable(params): params = list(params)
        if available(stdin) and not listable(stdin): stdin = list(stdin)
        if available(params) and available(stdin) and len(params) != len(stdin): raise RuntimeError('parameters and stdins size not match')
        if missing(params) and missing(stdin): raise RuntimeError('both parameters and stdins are missing')

        n = len(params)
        mpms = [(p, s) for p,s in zip(optional(params,[None]*n), optional(stdin,[None]*n))]
        _map = partial(pmap, nprocs = nprocs) if available(nprocs) else \
               partial(tmap, nthreads = nthreads) if available(nthreads) else smap
        return _map(mpms, self._exec)
