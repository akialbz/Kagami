#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
filesys

author(s): Albert (aki) Zhou
origin: 06-06-2016

"""


import logging, os, shutil
from kagami.core.prelim import NA, hasvalue
from kagami.core.functional import pick, drop


# file name manipulations
def filePath(fpath, absolute = True):
    p = fpath.rsplit(os.sep, 1)[0]
    return os.path.abspath(p) if absolute else p

def fileName(fpath):
    return fpath.rsplit(os.sep, 1)[-1]

def filePrefix(fpath):
    pts = fpath.rsplit('.', 1)
    return pts[0] if len(pts) == 1 or os.sep not in pts[-1] else fpath

def fileSuffix(fpath):
    pts = fpath.rsplit('.', 1)
    return pts[1] if len(pts) > 1 and os.sep not in pts[-1] else ''

def fileTitle(fpath):
    return filePrefix(fileName(fpath))


# search path
def listPath(path, recursive = False, fileOnly = False, folderOnly = False, visibleOnly = True, prefix = NA, suffix = NA):
    if fileOnly and folderOnly: logging.warning('nothing to expect after removing both dirs and files')

    fds = [os.path.join(root, name) for root, dirs, files in os.walk(path) for name in files + dirs] if recursive else \
          [os.path.join(path, name) for name in os.listdir(path)]

    if fileOnly: fds = pick(fds, os.path.isfile)
    if folderOnly: fds = pick(fds, os.path.isdir)
    if visibleOnly: fds = drop(fds, lambda x: fileName(x).startswith(('.', '~')))
    if hasvalue(prefix): fds = pick(fds, lambda x: fileName(x).startswith(prefix))
    if hasvalue(suffix): fds = pick(fds, lambda x: x.endswith(suffix))

    return fds


# check
def checkInputFile(fpath):
    if not os.path.isfile(fpath): raise IOError('input file [%s] not found' % fpath)
    if not os.path.getsize(fpath) > 0: logging.warning('input file [%s] is empty' % fpath)
    return fpath

def checkInputDir(dpath):
    if not os.path.isdir(dpath): raise IOError('input dir [%s] not found' % dpath)
    if not len(os.listdir(dpath)) > 0: logging.warning('input dir [%s] is empty' % dpath)
    return dpath

def checkOutputFile(fpath, override = True):
    if not os.path.isfile(fpath):
        checkOutputDir(os.path.dirname(fpath))
    elif override:
        logging.warning('output file [%s] already exists, override' % fpath)
        os.remove(fpath)
        if os.path.isfile(fpath): raise IOError('fail to remove existing output file [%s]' % fpath)
    return fpath

def checkOutputDir(dpath, override = False):
    if dpath.strip() != '':
        if os.path.isdir(dpath):
            if not override: return dpath
            logging.warning('output dir [%s] already exists, override' % dpath)
            shutil.rmtree(dpath)
            if os.path.isdir(dpath): raise IOError('fail to remove existing output dir [%s]' % dpath)
        os.makedirs(dpath)
        if not os.path.isdir(dpath): raise IOError('fail to create output dir [%s]' % dpath)
    return dpath

