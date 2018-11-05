#!/usr/bin/env python
#  -*- coding: utf-8 -*-

import setuptools
from kagami.portals import configPortal
from kagami import __version__, __version_name__

def _parse_requires(pipfile = 'Pipfile'):
    pcfg = configPortal.load(pipfile, autoEval = False)
    reqs = [k if v == '"*"' else (k+v.strip('"')) for k,v in pcfg['packages'].items()]
    return reqs

with open('README.md', 'r') as fh:
    long_description = fh.read()
    setuptools.setup(
        name             = 'kagami',
        version          = __version__,
        author           = 'Albert Zhou',
        author_email     = 'j.zhou.3@bham.ac.uk',
        url              = 'https://github.com/albert500/Kagami',
        packages         = setuptools.find_packages(),
        description      = 'The Kagami library (%s)' % __version_name__,
        long_description = long_description,
        long_description_content_type = 'text/markdown',
        classifiers = [
            'Topic:: Scientific / Engineering:: Bio - Informatics',
            'Topic :: Software Development :: Libraries',
            'Programming Language :: Python :: 2',
            'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
            'Operating System :: POSIX',
        ],
        install_requires = _parse_requires()
    )
