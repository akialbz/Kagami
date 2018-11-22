#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
test_textPortal

author(s): Albert (aki) Zhou
origin: 11-22-2018

"""


import os
import numpy as np
from string import ascii_letters, join
from kagami.core import *
from kagami.portals import textPortal


def _createlns():
    chars = [c for c in ascii_letters + '`~!@#$%^&*()_+-={}[]|\\:;"\'<,>./?']
    dm = np.random.choice(chars, size = (50, 10))
    return smap(dm, lambda ln: join(ln, ''))

def test_text_io():
    otx = join(_createlns(), '\n')
    fn = 'test_text_portal.txt'

    textPortal.save(otx, fn)
    assert os.path.isfile(fn)

    itx = textPortal.load(fn)
    assert itx == otx

    os.remove(fn)

def test_textlns_io():
    olns = _createlns()
    fn = 'test_text_portal.txt'

    textPortal.savelns(olns, fn, autoReturn = True)
    assert os.path.isfile(fn)

    ilns = textPortal.loadlns(fn, striping = False)
    assert checkall(zip(ilns, olns), unpack(lambda il, ol: il == ol))

    os.remove(fn)
