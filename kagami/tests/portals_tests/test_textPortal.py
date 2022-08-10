#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
test_textPortal

author(s): Albert (aki) Zhou
added: 11-22-2018

"""


import numpy as np
from pathlib import Path
from string import ascii_letters
from kagami.comm import *
from kagami.portals import textPortal


def _createlns():
    chars = [c for c in ascii_letters + '`~!@#$%^&*()_+-={}[]|\\:;"\'<,>./?']
    dm = np.random.choice(chars, size = (50, 10))
    return smap(dm, lambda ln: paste(ln, sep = ''))

def test_text_io():
    otx = paste(_createlns(), '\n')
    fn = Path('test_text_portal.txt')

    textPortal.save(otx, fn)
    assert fn.is_file()
    itx = textPortal.load(fn)
    assert itx == otx

    fn.unlink()

def test_textlns_io():
    olns = _createlns()
    fn = Path('test_text_portal.txt')

    textPortal.savelns(olns, fn, newline = '\n')
    assert fn.is_file()
    ilns = textPortal.loadlns(fn, strip = False)
    assert checkall(zip(ilns, olns), unpack(lambda il, ol: il == ol))

    fn.unlink()
