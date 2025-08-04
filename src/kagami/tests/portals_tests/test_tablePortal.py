#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
test_tablePortal

author(s): Albert (aki) Zhou
added: 11-22-2018

"""


import numpy as np
from pathlib import Path
from kagami.comm import *
from kagami.portals import tablePortal


def _createdm():
    hd = ['# test headline 1',
          '# test headline 2',
          '-------']
    dm = [['c1', 'c"2', '"c"3', "c'4", "'c'5", 'c,6', 'c 7', ',c8', 'c9,', ' c10 ']] + \
         smap(np.random.randint(0, 10, size = (5, 10)), lambda ln: smap(ln,str)) + \
         [['# test comments']]
    return hd, dm

def test_general_io():
    ohd, odm = _createdm()
    fn = Path('test_table_portal.txt')

    tablePortal.save(odm, fn, heads = ohd, delimiter = ' ')
    assert fn.is_file()
    idm = tablePortal.load(fn, skips = len(ohd), comment = '#', delimiter = ' ')
    assert np.all(np.array(idm) == np.array(odm[:-1]))

    fn.unlink()

def test_csv_io():
    ohd, odm = _createdm()
    fn = Path('test_table_portal.csv')

    tablePortal.savecsv(odm, fn, heads = ohd)
    assert fn.is_file()
    idm = tablePortal.loadcsv(fn, skips = len(ohd), comment = '#')
    assert np.all(np.array(idm) == np.array(odm[:-1]))

    fn.unlink()

def test_tsv_io():
    ohd, odm = _createdm()
    fn = Path('test_table_portal.tsv')

    tablePortal.savetsv(odm, fn, heads = ohd)
    assert fn.is_file()
    idm = tablePortal.loadtsv(fn, skips = len(ohd), comment = '#')
    assert np.all(np.array(idm) == np.array(odm[:-1]))

    fn.unlink()


