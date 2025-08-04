#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
unitest

author(s): Albert (aki) Zhou
added: 11-06-2018

"""


import os


def test(kind = 'self', *, capture = True, cov = False, covReport = False, profile = False, profileSVG = False,
         pyargs = ('-W ignore::tables.exceptions.FlavorWarning',)): # pragma: no cover
    assert kind in ('self', 'fast', 'full'), f'unknown testing name {kind}'

    try:
        import pytest
    except ImportError:
        raise ImportError('unit tests require pytest (>= 5.3.2), pytest-cov (>= 2.8.1, optional) and pytest-profiling (>= 1.7.0, optional)')

    if kind != 'self':
        print('running dependencies-testing ...')

        print('testing numpy ...')
        import numpy; numpy.test(kind)
        print('\n\n')

        print('testing scipy ...')
        try:
            import scipy
            scipy.test(kind)
        except ImportError:
            pass
        print('\n\n')

        print('testing rpy2 ...')
        try:
            import rpy2
            # pytest.main(["--pyargs",  "rpy2.tests"])
            pytest.main(["--pyargs",  "rpy2.tests", "-k", "not test_timeR2Pandas"]) # rpy2 3.4.5 not compatible with latest pandas datetimes
        except ImportError:
            pass
        print('\n\n')

        print('finished dependencies-testing\n\n')

    print('running self-testing ...')

    pms = list(pyargs)
    if not capture: pms += ['--capture=no']
    if cov:
        pms += ['--cov=kagami']
        if covReport: pms += ['--cov-report html']
    if profile:
        pms += ['--profile']
        if profileSVG: pms += ['--profile-svg']
    ret = pytest.main([os.path.dirname(os.path.realpath(__file__))] + pms)

    print('finished self-testing with return code [%s]' % str(ret))
    return ret

