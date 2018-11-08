#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
unitest

author(s): Albert (aki) Zhou
origin: 11-06-2018

"""


import os, pytest


def test(showOutput = False, showCov = False, covReport = False, showProfile = False, profileSVG = False, pyargs = ()):
    pms = list(pyargs)
    if showOutput: pms += ['--capture=no']
    if showCov:
        pms += ['--cov=kagami']
        if covReport: pms += ['--cov-report html']
    if showProfile:
        pms += ['--profile']
        if profileSVG: pms += ['--profile-svg']
    pytest.main([os.path.dirname(os.path.realpath(__file__))] + pms)
