#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
test_configPortal

author(s): Albert (aki) Zhou
origin: 11-22-2018

"""


import os
from kagami.core import *
from kagami.portals import textPortal, configPortal


_cfgs = '''
[section 1]
val1 = 1
val2 = True
val3 = ['a', 'b']
val4 = (5, 6)

[section 2]
val1 = ''
val2 = 
val3 = None
val4 = NA
val5 = N/A

'''

def test_config_io():
    fn = 'test_config_portal.cfg'

    textPortal.save(_cfgs, fn)
    cfgs = configPortal.load(fn, autoEval = True, emptyAsMissing = True)

    assert set(cfgs.keys()) == {'section 1', 'section 2'}
    assert cfgs['section 1'] == {'val1': 1, 'val2': True, 'val3': ['a', 'b'], 'val4': (5, 6)}
    assert cfgs['section 2'] == {'val1': '', 'val2': na, 'val3': None, 'val4': na, 'val5': na}

    os.remove(fn)
