#!/usr/bin/env python
"""The Kagami packages"""


import setuptools, json
from kagami import __version__


def _parse_requires():
    with open('requirements.txt') as f: requirements = f.read().splitlines()
    return requirements

def _build_version(verfile = '.buildversion'):
    with open(verfile, 'r') as f: vers = json.load(f)
    vers['main'], vers['build'] = __version__, 0 if vers['main'] != __version__ else vers['build'] + 1
    with open(verfile, 'w') as f: json.dump(vers, f)
    return vers['main'] + '.' + str(vers['build'])

reqs = _parse_requires()

with open('README.md', 'r') as fh:
    long_description = fh.read()
    setuptools.setup(
        name             = 'kagami',
        version          =  _build_version(),
        author           = 'Albert Zhou',
        url              = 'https://github.com/akialbz/Kagami',
        packages         = setuptools.find_packages(),
        description      = 'A framework to support functional programming for computational biology algorithm development',
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
