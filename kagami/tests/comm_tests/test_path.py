#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
test_path

author(s): Albert (aki) Zhou
added: 11-21-2018

"""


import os, shutil, pytest
from pathlib import Path
from kagami.comm import *


def test_file_names():
    fn = Path(__file__)
    assert filePath(fn, absolute = False) == str(fn.parent)
    assert filePath(fn, absolute = True) == str(fn.parent.absolute())
    assert fileName(fn) == str(fn.name)
    assert filePrefix(fn) == str(fn)[:-3]
    assert fileSuffix(fn) == str(fn.suffix)
    assert fileTitle(fn) == str(fn.stem)

    fn1 = '/path/to/file.ex1.ex2'
    fn2 = '/file'
    assert filePath(fn1) == '/path/to' and filePath(fn2) == '/'
    assert fileName(fn1) == 'file.ex1.ex2' and fileName(fn2) == 'file'
    assert filePrefix(fn1) == '/path/to/file.ex1' and filePrefix(fn2) == '/file'
    assert fileSuffix(fn1) == '.ex2' and fileSuffix(fn2) == ''
    assert fileTitle(fn1) == 'file.ex1' and fileTitle(fn2) == 'file'

def test_listpath():
    pys = listPath(filePath(__file__), recursive = False, fileonly = True, visible = True, suffix = '.py')
    assert set(smap(pys, fileTitle)) == {'__init__', 'test_misc', 'test_types', 'test_functional', 'test_path'}
    pys = listPath(Path(__file__).parent.parent, recursive = True, dironly = True, visible = True)
    assert set(smap(pys, fileTitle)) == {'comm_tests', 'dtypes_tests', 'portals_tests', 'wrappers_tests', '__pycache__'}

def test_removepath():
    fname = 'test_path_file'
    with open(fname, 'w') as f: f.write('')
    assert removePath(fname) == True
    assert not os.path.isfile(fname)

    dname = 'test_path_dir/'
    os.makedirs(dname)
    assert removePath(dname) == True
    assert not os.path.isdir(dname)

def test_checks():
    with pytest.raises(IOError): checkInputFile('no_such_file')
    assert checkInputFile(__file__) is None

    with pytest.raises(IOError): checkInputDir('no_such_dir')
    assert checkInputDir(filePath(__file__)) is None

    rmfile = Path(filePath(__file__)) / 'test_remove_file'
    with open(rmfile, 'w+') as f: f.write('')
    assert rmfile.is_file()
    checkOutputFile(rmfile)
    assert not rmfile.is_file()

    rmfold = Path(filePath(__file__)) / 'test_remove_folder'
    checkOutputDir(rmfold)
    assert rmfold.is_dir()
    checkOutputDir(rmfold, override = True)
    assert rmfold.is_dir()
    shutil.rmtree(rmfold)

