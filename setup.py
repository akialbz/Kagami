#!/usr/bin/env python
#  -*- coding: utf-8 -*-

import sys, setuptools
from kagami.portals import configPortal
from kagami import __version__, __version_name__

def _parse_requires(pipfile = 'Pipfile', exclude = ()):
    pcfg = configPortal.load(pipfile, autoEval = False)
    reqs = [k if v == '"*"' else (k+v.strip('"')) for k,v in pcfg['packages'].items() if k not in exclude]
    return reqs

def _build_version(verfile = '.buildversion'):
    with open(verfile, 'r+') as f:
        bver = f.read()
        bver = 0 if bver == '' else int(bver)
        f.seek(0)
        f.write(str(bver + 1))
        f.truncate()
    return bver

if "--no-rpy" in sys.argv:
    reqs = _parse_requires(exclude = ('rpy2',))
    sys.argv.remove("--no-rpy")
else:
    reqs = _parse_requires()

with open('README.md', 'r') as fh:
    long_description = fh.read()
    setuptools.setup(
        name             = 'kagami',
        version          = __version__ + '.%d' % _build_version(),
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
        install_requires = reqs
    )
