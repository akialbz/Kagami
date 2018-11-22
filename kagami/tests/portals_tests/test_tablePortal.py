#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
test_tablePortal

author(s): Albert (aki) Zhou
origin: 11-22-2018

"""


import os
import numpy as np
from kagami.core import *
from kagami.portals import tablePortal


def _createdm():
    hd = [
        '# test headline 1',
        '# test headline 2',
        ''
    ]
    dm = [['c1', 'c"2', '"c"3', "c'4", "'c'5", 'c,6', 'c 7', ',c8', 'c9,', ' c10 ']] + \
         smap(np.random.randint(0, 10, size = (5, 10)), lambda ln: smap(ln,str))
    return hd, dm

def test_csv_io():
    ohd, odm = _createdm()
    fn = 'test_table_portal.csv'

    tablePortal.savecsv(odm, fn, heads = ohd)
    assert os.path.isfile(fn)

    ihd, idm = tablePortal.loadcsv(fn, headRows = len(ohd), wrap = np.array)
    assert checkall(zip(ohd, ihd), unpack(lambda oh,ih: oh == ih))
    assert np.all(np.array(idm) == np.array(odm))

    os.remove(fn)

def test_tsv_io():
    ohd, odm = _createdm()
    fn = 'test_table_portal.tsv'

    tablePortal.save(odm, fn, heads = ohd, delimiter = '\t')
    assert os.path.isfile(fn)

    ihd, idm = tablePortal.load(fn, headRows = len(ohd), wrap = np.array, delimiter = '\t')
    assert checkall(zip(ohd, ihd), unpack(lambda oh,ih: oh == ih))
    assert np.all(np.array(idm) == np.array(odm))

    os.remove(fn)


