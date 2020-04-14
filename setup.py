#!/usr/bin/env python
#  -*- coding: utf-8 -*-

import sys, setuptools, json
from kagami import __version__, __version_name__
from kagami.comm import drop

def _parse_requires():
    with open('requirements.txt') as f: requirements = f.read().splitlines()
    return requirements

def _build_version(verfile = '.buildversion'):
    with open(verfile, 'r') as f: vers = json.load(f)
    vers['main'], vers['build'] = __version__, 0 if vers['main'] != __version__ else vers['build'] + 1
    with open(verfile, 'w') as f: json.dump(vers, f)
    return vers['main'] + '.' + str(vers['build'])

reqs = _parse_requires()
if "--no-rwrapper" in sys.argv:
    reqs = drop(reqs, lambda x: x.startswith('rpy2'))
    sys.argv.remove("--no-rwrapper")

with open('README.md', 'r') as fh:
    long_description = fh.read()
    setuptools.setup(
        name             = 'kagami',
        version          =  _build_version(),
        author           = 'Albert Zhou',
        author_email     = 'j.zhou.3@bham.ac.uk',
        url              = 'https://github.com/albert500/Kagami',
        packages         = setuptools.find_packages(),
        description      = 'The Kagami library (%s)' % __version_name__,
        long_description = long_description,
        long_description_content_type = 'text/markdown',
        classifiers = [
            'Topic :: Scientific/Engineering :: Bio-Informatics',
            'Topic :: Software Development :: Libraries',
            'Programming Language :: Python :: 3',
            'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
            'Operating System :: POSIX',
        ],
        install_requires = reqs
    )
