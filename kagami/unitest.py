#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
unitest

author(s): Albert (aki) Zhou
origin: 11-06-2018

"""


import os, pytest


def test(capture = False, cov = False, covReport = False, profile = False, profileSVG = False, pyargs = ()):
    pms = list(pyargs)
    if not capture: pms += ['--capture=no']
    if cov:
        pms += ['--cov=kagami']
        if covReport: pms += ['--cov-report html']
    if profile:
        pms += ['--profile']
        if profileSVG: pms += ['--profile-svg']
    pytest.main([os.path.dirname(os.path.realpath(__file__))] + pms)
