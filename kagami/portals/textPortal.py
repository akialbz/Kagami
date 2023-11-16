#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
textPortal

author(s): Albert (aki) Zhou
added: 06-28-2014

"""


import os
from typing import List, Iterable, Union, Optional
from pathlib import Path
from kagami.comm import available, smap, pickmap, drop, checkInputFile, checkOutputFile


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

def savelns(lines: Iterable[str], fname: Union[str, Path], mode: str = 'w', newline: Optional[str] = '\n') -> bool:
    checkOutputFile(fname)
    lines = smap(lines, str)
    if available(newline): lines = pickmap(lines, lambda x: x == '' or x[-1] != newline, lambda x: x + newline)
    with open(fname, mode) as ofile: ofile.writelines(lines)
    return os.path.isfile(fname)
