#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
misc

author(s): Albert (aki) Zhou
added: 06-07-2016

"""


from typing import Any
from .types import iterable


__all__ = [
    'T', 'F', 'paste',
]


# R-like components
T = True
F = False

def paste(*args: Any, sep: str = '') -> str:
    if len(args) == 1 and iterable(args[0]): args = args[0]
    return sep.join([str(v) for v in args])
