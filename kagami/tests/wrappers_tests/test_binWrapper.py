#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
test_binWrapper

author(s): Albert (aki) Zhou
origin: 11-22-2018

"""


import os, pytest
from kagami.core import *
from kagami.wrappers import BinaryWrapper


@pytest.mark.skipif(os.name != 'posix', reason = 'BinaryWrapper is designed for POSIX only')
def test_stats():
    assert BinaryWrapper.which('sh') == os.popen('which sh').read().rstrip('\n')
    assert BinaryWrapper.which('no-such-executable') is None

    assert BinaryWrapper.reachable('sh') == True
    assert BinaryWrapper.reachable('no-such-executable') == False

@pytest.mark.skipif(os.name != 'posix', reason = 'BinaryWrapper is designed for POSIX only')
def test_runs():
    bw = BinaryWrapper('ls')
    flst = set(smap(listPath(filePath(__file__), recursive = False, fileOnly = True, suffix = '.py'), fileName))

    rcode, (rstd, rerr) = bw.execute([ filePath(__file__) ])
    assert rcode == 0 and rerr == '' and \
           set(pick(rstd.strip().split('\n'), lambda x: x.endswith('.py'))) == flst

    def _testmap(nt = na, np = na):
        rcodes, rstrs = zip(*bw.mapexec([[filePath(__file__)] for _ in range(3)], nthreads = nt, nprocs = np))
        rstds, rerrs = zip(*rstrs)
        assert set(rcodes) == {0} and set(rerrs) == {''} and \
               set(collapse(smap(rstds, lambda rs: pick(rs.strip().split('\n'), lambda x: x.endswith('.py'))))) == flst
    _testmap()
    _testmap(nt = 3)
    _testmap(np = 3)
