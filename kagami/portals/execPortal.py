#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
execPortal: portals to manipulate binary executables

WARNING: designed for macOS / linux, may encounter problems in windows

author(s): Albert Zhou
origin: 01-25-2016

"""


import logging, os
from multiprocessing.pool import ThreadPool, cpu_count
from string import join, strip
from subprocess import Popen, PIPE
from ..prelim import checkany, NA, optional, hasvalue
from ..functional import pipe, do, drop, composite, partial


def checkBinary(exe):
    if os.name == 'nt':
        logging.warning('execPortal is designed and tested for macOS / linux, may encounter problems on windows')
    if exe.startswith('./'): exe = exe[2:]
    ext = checkany([''] + pipe(os.environ['PATH'].split(':') | drop(lambda x: x.strip() == ''), list),
                   lambda p: os.path.isfile(os.path.join(p.strip(), exe)))
    logging.debug('executable [%s] %s in $PATH' % (exe, 'found' if ext else 'not found'))
    return ext

def execBinary(exe, params = NA, inStream = NA, inShell = False, mute = False, normalRetCode = 0):
    if not checkBinary(exe): raise RuntimeError('executable binary [%s] not found' % exe)

    pms = [] if not hasvalue(params) else \
          [params] if type(params) in (str, unicode) else \
          pipe(params | do(composite(str, strip)) | drop(lambda v: len(v) == 0))

    cmd = ([exe] + pms) if not inShell else \
          (exe + ' ' + pipe(pms | do(lambda x: x.replace(' ', '\ ')), partial(join, sep = ' ')))
    logging.debug('cmd = [%s]' % (cmd if type(cmd) == str else join(cmd, ' ')))

    proc = Popen(cmd, stdin = PIPE, stdout = PIPE, stderr = PIPE, shell = inShell)
    rstrs = proc.communicate(input = optional(inStream))
    rmsgs = pipe(rstrs | do(lambda x: '' if x is None else x.strip()), partial(join, sep = ''))
    rcode = proc.returncode

    if rcode == normalRetCode:
        logging.log((logging.DEBUG if mute else logging.INFO), rmsgs)
    else:
        logging.error('execution failed [%d]:\n%s' % (rcode, rmsgs))
    return rcode, rmsgs

def execBinaryBatch(exe, paramsList, inStreamList = NA, inShell = False, mute = False, normalRetCode = 0, procs = NA):
    if hasvalue(inStreamList) and len(paramsList) != len(inStreamList):
        raise ValueError('inStream list and parameters list size not match')
    if not hasvalue(procs): procs = cpu_count() - 1

    def _poolmap(ps):
        pool = ThreadPool(processes = procs)
        jobs = [pool.apply_async(execBinary, p) for p in ps]
        pool.close()
        pool.join()
        return [j.get() for j in jobs]

    def _singlemap(ps):
        return map(lambda p: execBinary(*p), ps)

    pmls = [(exe, pms, ins, inShell, mute, normalRetCode)
            for pms, ins in zip(paramsList, optional(inStreamList, [NA] * len(paramsList)))]
    return (_singlemap if procs < 2 else _poolmap)(pmls)
