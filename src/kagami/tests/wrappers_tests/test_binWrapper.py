#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
test_binWrapper

author(s): Albert (aki) Zhou
added: 11-22-2018

"""


import os, pytest
from kagami.comm import *
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
    flst = set(smap(listPath(filePath(__file__), recursive = False, fileonly = True, suffix = '.py'), fileName))

    rcode, (rstd, rerr) = bw.execute([ filePath(__file__) ], timeout = 10)
    assert rcode == 0 and rerr == '' and \
           set(pick(rstd.strip().split('\n'), lambda x: x.endswith('.py'))) == flst

    bw = BinaryWrapper('sleep')
    with pytest.raises(RuntimeError): rcode, _ = bw.execute([3], timeout = 1)

    bw = BinaryWrapper('sleep', normcodes = [0, 124])
    assert bw.execute([3], timeout = 1)[0] == 124

@pytest.mark.skipif(os.name != 'posix', reason = 'BinaryWrapper is designed for POSIX only')
def test_mapruns():
    bw = BinaryWrapper('ls')
    flst = set(smap(listPath(filePath(__file__), recursive = False, fileonly = True, suffix = '.py'), fileName))

    def _testmap(nt = None, np = None, to = None):
        rcodes, rstrs = zip(*bw.mapexec([[filePath(__file__)] for _ in range(3)], nthreads = nt, nprocs = np, timeout = to))
        rstds, rerrs = zip(*rstrs)
        assert set(rcodes) == {0} and set(rerrs) == {''} and \
               set(collapse(smap(rstds, lambda rs: pick(rs.strip().split('\n'), lambda x: x.endswith('.py'))))) == flst

    _testmap()
    _testmap(to = 10)
    _testmap(nt = 3)
    _testmap(np = 3)
    _testmap(nt = 3, to = 10)
    _testmap(np = 3, to = 10)

