#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
__init__

author(s): Albert (aki) Zhou
added: 03-18-2017

"""


from importlib.metadata import version
__version__ = version('kagami')
__version_name__ = 'Kaga'


from .unitest import test
