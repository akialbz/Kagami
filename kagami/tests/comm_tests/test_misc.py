#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
test_etc.py

author(s): Albert (aki) Zhou
origin: 11-14-2018

"""


from kagami.comm import *


def test_rlikes():
    assert T == True
    assert F == False
    assert paste(1, 2, 3, sep = ',') == '1,2,3'
    assert paste(*['a', 'b', 'c']) == 'abc'
