#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
test_path

author(s): Albert (aki) Zhou
origin: 11-21-2018

"""


import os, shutil, pytest
from kagami.core import *


def test_file_names():
    fn = os.path.abspath(__file__)
    assert filePath(fn) == os.path.dirname(os.path.abspath(__file__))
    assert fileName(fn) == os.path.basename(__file__)
    assert filePrefix(fn) == os.path.join(os.path.dirname(os.path.abspath(__file__)), os.path.basename(__file__).rsplit('.',1)[0])
    assert fileSuffix(fn) == __file__.rsplit('.',1)[-1]
    assert fileTitle(fn) == os.path.basename(__file__).rsplit('.',1)[0]

    fn1 = '/path/to/file.ex1.ex2'
    fn2 = '/file'
    assert filePath(fn1) == '/path/to' and filePath(fn2) == '/'
    assert fileName(fn1) == 'file.ex1.ex2' and fileName(fn2) == 'file'
    assert filePrefix(fn1) == '/path/to/file.ex1' and filePrefix(fn2) == '/file'
    assert fileSuffix(fn1) == 'ex2' and fileSuffix(fn2) == ''
    assert fileTitle(fn1) == 'file.ex1' and fileTitle(fn2) == 'file'

def test_listpath():
    pys = listPath(filePath(__file__), recursive = True, fileOnly = True, visibleOnly = True, suffix = '.py')
    assert set(smap(pys, fileTitle)) == {'__init__', 'test_etc', 'test_optvalue', 'test_metadata', 'test_functional', 'test_path'}

def test_checks():
    with pytest.raises(IOError): checkInputFile('no_such_file')
    assert checkInputFile(__file__) == __file__

    with pytest.raises(IOError): checkInputDir('no_such_dir')
    assert checkInputDir(filePath(__file__)) == filePath(__file__)

    rmfile = os.path.join(filePath(__file__), 'test_remove_file')
    with open(rmfile, 'w+') as f: f.write('')
    assert os.path.isfile(rmfile)
    checkOutputFile(rmfile)
    assert not os.path.isfile(rmfile)

    rmfold = os.path.join(filePath(__file__), 'test_remove_folder')
    checkOutputDir(rmfold)
    assert os.path.isdir(rmfold)
    checkOutputDir(rmfold, override = True)
    assert os.path.isdir(rmfold)
    shutil.rmtree(rmfold)

