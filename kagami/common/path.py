#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
path

author(s): Albert (aki) Zhou
origin: 06-06-2016

"""


import logging, os, shutil
from pathlib import Path
from typing import Union, List, Optional
from .types import missing, optional, isstring
from .functional import pick, drop


__all__ = [
    'filePath', 'fileName', 'filePrefix', 'fileSuffix', 'fileTitle', 'listPath',
    'checkInputFile', 'checkInputDir', 'checkOutputFile', 'checkOutputDir'
]


# file name manipulations
def filePath(fpath: Union[str, Path], absolute: bool = True) -> str:
    if isstring(fpath): fpath = Path(fpath)
    pth = fpath.parent
    return str(pth.absolute() if absolute else pth)

def fileName(fpath: Union[str, Path]) -> str:
    if isstring(fpath): fpath = Path(fpath)
    return fpath.name

def filePrefix(fpath: Union[str, Path], absolute: bool = True) -> str:
    if isstring(fpath): fpath = Path(fpath)
    return str(fpath.absolute() if absolute else fpath)[:-len(fpath.suffix)]

def fileSuffix(fpath: Union[str, Path]) -> str:
    if isstring(fpath): fpath = Path(fpath)
    return fpath.suffix

def fileTitle(fpath: Union[str, Path]) -> str:
    if isstring(fpath): fpath = Path(fpath)
    return fpath.stem


# search path
def listPath(path: Union[str, Path], *, recursive: bool = False, fileonly: bool = False, dironly: bool = False,
             visible: bool = True, prefix: Optional[str] = None, suffix: Optional[str] = None, globptn: Optional[str] = None) -> List[Path]:
    if fileonly and dironly: logging.warning('nothing to expect after excluding both dirs and files')

    if missing(globptn): globptn = ('**/' if recursive else '*/') + optional(prefix, '') + '*' + optional(suffix, '')
    if isstring(path): path = Path(path)
    fds = list(path.glob(globptn))

    if fileonly: fds = pick(fds, lambda x: x.is_file())
    if dironly:  fds = pick(fds, lambda x: x.is_dir())
    if visible:  fds = drop(fds, lambda x: fileName(x).startswith('.'))
    return fds

def removePath(path: Union[str, Path]) -> None:
    if isstring(path): path = Path(path)
    if path.is_file(): path.unlink()
    else: shutil.rmtree(path)


# check
def checkInputFile(fpath: Union[str, Path]) -> None:
    if isstring(fpath): fpath = Path(fpath)
    if not fpath.is_file(): raise IOError(f'input file [{fpath}] not found')
    if not fpath.stat().st_size > 0: logging.warning('input file [%s] is empty', fpath)

def checkInputDir(dpath: Union[str, Path]) -> None:
    if isstring(dpath): dpath = Path(dpath)
    if not dpath.is_dir(): raise IOError(f'input dir [{dpath}] not found')
    if not len(list(dpath.glob('**/*'))) > 0: logging.warning('input dir [%s] is empty', dpath)

def checkOutputFile(fpath: Union[str, Path], override: bool = True) -> None:
    if isstring(fpath): fpath = Path(fpath)
    if not fpath.is_file(): checkOutputDir(fpath.parent)
    if not override: return
    logging.warning('output file [%s] already exists, override', fpath)
    fpath.unlink()
    if fpath.is_file(): raise IOError(f'fail to remove existing output file [{fpath}]')

def checkOutputDir(dpath: Union[str, Path], override: bool = False) -> None:
    if isstring(dpath): dpath = Path(dpath)
    if dpath.samefile(Path.cwd()): return
    if dpath.is_dir():
        if not override: return
        logging.warning('output dir [%s] already exists, override', dpath)
        shutil.rmtree(dpath)
    os.makedirs(dpath, exist_ok = False)
    if not dpath.is_dir(): raise IOError(f'fail to create output dir [{dpath}]')

