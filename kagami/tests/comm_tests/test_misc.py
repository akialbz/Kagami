#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
test_etc.py

author(s): Albert (aki) Zhou
added: 11-14-2018

"""


import numpy as np
import pytest
from kagami.comm import *


def test_rlikes():
    assert T == True
    assert F == False
    assert paste(1, 2, 3, sep = ',') == '1,2,3'
    assert paste(*['a', 'b', 'c']) == 'abc'
    assert paste(iter(['a', 'b', 'c'])) == 'abc'

def test_checks():
    assert checkall(np.ones(10), lambda x: x == 1) and not checkall(iter([1,0,1,1,1]), lambda x: x == 1)
    assert checkany(iter([1,0,1,1,1]), lambda x: x == 1) and not checkany(np.ones(10), lambda x: x != 1)

def test_validarg():
    assert validarg('a', ('a', 'b', 'c')) == 'a'
    with pytest.raises(ValueError): validarg('a', ('b', 'c'))

def test_unique():
    x = np.random.randint(-50, 50, size = 100)
    ux, ucnt = np.unique(x, return_counts = True)
    sx, scnt = unique(x, return_counts = True)
    assert len(ux) == len(sx)
    assert np.all(ux == np.sort(sx))
    assert len(ucnt) == len(scnt)
    assert np.all(ucnt == scnt[np.argsort(sx)])
