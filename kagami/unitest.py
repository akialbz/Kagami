#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
unitest

author(s): Albert (aki) Zhou
added: 11-06-2018

"""


import logging
import os


def test(capture = True, cov = False, covReport = False, profile = False, profileSVG = False,
         pyargs = ('-W ignore::tables.exceptions.FlavorWarning',)): # pragma: no cover
    try:
        import pytest
    except ImportError:
        raise ImportError('unit tests require pytest (>= 5.3.2), pytest-cov (>= 2.8.1, optional) and pytest-profiling (>= 1.7.0, optional)')

    logging.debug('running self-testing ...')

    pms = list(pyargs)
    if not capture: pms += ['--capture=no']
    if cov:
        pms += ['--cov=kagami']
        if covReport: pms += ['--cov-report html']
    if profile:
        pms += ['--profile']
        if profileSVG: pms += ['--profile-svg']
    ret = pytest.main([os.path.dirname(os.path.realpath(__file__))] + pms)

    logging.debug('finished self-testing with return code [%s]' % str(ret))
    return ret

