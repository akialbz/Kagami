#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
textPortal

author(s): Albert (aki) Zhou
origin: 06-28-2014

"""


import os
from typing import List, Iterable, Union
from pathlib import Path
from kagami.comm import smap, drop, checkInputFile, checkOutputFile


__all__ = ['load', 'save', 'loadlns', 'savelns']


# raw text string
def load(fname: Union[str, Path], mode: str = 'r') -> str:
    checkInputFile(fname)
    with open(fname, mode) as f: txt = f.read()
    return txt

def save(txt: str, fname: Union[str, Path], mode: str = 'w') -> bool:
    checkOutputFile(fname)
    with open(fname, mode) as f: f.write(txt)
    return os.path.isfile(fname)


# raw text lines
def loadlns(fname: Union[str, Path], mode: str = 'r', strip: bool = True) -> List[str]:
    checkInputFile(fname)
    with open(fname, mode) as f: lns = f.readlines()
    lns = smap(lns, lambda x: x.rstrip('\n'))
    if strip: lns = drop(lns, lambda x: x.strip() == '')
    return lns

def savelns(lines: Iterable[str], fname: Union[str, Path], mode = 'w', newline = True) -> bool:
    checkOutputFile(fname)
    if newline: lines = smap(lines, lambda x: x.rstrip('\n') + '\n')
    with open(fname, mode) as ofile: ofile.writelines(lines)
    return os.path.isfile(fname)
