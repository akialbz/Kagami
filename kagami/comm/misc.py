#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
misc

author(s): Albert (aki) Zhou
origin: 06-07-2016

"""


from typing import Any


__all__ = [
    'T', 'F', 'paste',
]


# R-like components
T = True
F = False

def paste(*args: Any, sep: str = '') -> str:
    return sep.join([str(v) for v in args])

