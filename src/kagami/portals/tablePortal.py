#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
tablePortal

author(s): Albert (aki) Zhou
added: 06-28-2014

"""


import os, csv
from pathlib import Path
from typing import List, Iterable, Union, Optional, Any
from kagami.comm import l, available, pickmap, drop, partial, checkInputFile, checkOutputFile


__all__ = ['load', 'save', 'loadcsv', 'savecsv', 'loadtsv', 'savetsv']


# general portals
def load(fname: Union[str, Path], *, mode: str = 'r',
         skips: Optional[int] = None, comment: Optional[str] = None, strip: bool = False, **kwargs: Any) -> List[List[str]]:
    checkInputFile(fname)
    with open(fname, mode) as f:
        if available(skips) and skips > 0:
            for _ in range(skips): next(f)
        tb = csv.reader(f, **kwargs)
        if strip: tb = drop(tb, lambda x: len(x) == 0 or (len(x) == 1 and x[0].strip() == ''))
        if available(comment): tb = drop(tb, lambda x: x[0].startswith(comment))
        tb = l(tb)
    return tb

def save(table: Iterable[Iterable[str]], fname: Union[str, Path], *, mode: str = 'w',
         heads: Optional[Iterable[str]] = None, **kwargs: Any) -> bool:
    checkOutputFile(fname)
    with open(fname, mode) as f:
        if available(heads): f.writelines(pickmap(heads, lambda x: x[-1] != '\n', lambda x: x + '\n'))
        csv.writer(f, **kwargs).writerows(table)
    return os.path.isfile(fname)


# csv / tsv portals
loadcsv = partial(load, delimiter = ',')
savecsv = partial(save, delimiter = ',')

loadtsv = partial(load, delimiter = '\t')
savetsv = partial(save, delimiter = '\t')
