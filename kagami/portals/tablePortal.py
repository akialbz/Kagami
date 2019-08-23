#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
tablePortal

author(s): Albert (aki) Zhou
origin: 06-28-2014

"""


import os, csv
from pathlib import Path
from typing import List, Iterable, Union, Optional, Any
from kagami.common import l, available, smap, drop, partial, checkall, checkInputFile, checkOutputFile


__all__ = ['load', 'save', 'loadcsv', 'savecsv']


# csv portals
def loadcsv(fname: Union[str, Path], *, mode: str = 'r',
            skips: Optional[int] = 0, comment: Optional[str] = '#', strip: bool = True,
            **kwargs: Any) -> List[List[str]]:
    checkInputFile(fname)
    with open(fname, mode) as f:
        if available(skips) and skips > 0:
            for _ in range(skips): next(f)
        tb = csv.reader(f, **kwargs)
        if strip: tb = drop(tb, lambda x: len(x) == 0 or checkall(x, lambda v: v.strip() == ''))
        if available(comment): tb = drop(tb, lambda x: x[0].startswith(comment))
        tb = l(tb)
    return tb

def savecsv(table: Iterable[Iterable[str]], fname: Union[str, Path], *, mode: str = 'w',
            heads: Optional[Iterable[str]] = None, **kwargs: Any) -> bool:
    checkOutputFile(fname)
    with open(fname, mode) as f:
        if available(heads): f.writelines(smap(heads, lambda x: x.rstrip('\n') + '\n'))
        csv.writer(f, **kwargs).writerows(table)
    return os.path.isfile(fname)


# general / tsv portals
load = partial(loadcsv, delimiter = '\t')

save = partial(savecsv, delimiter = '\t')

