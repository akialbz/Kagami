#!/usr/bin/env python
#  -*- coding: utf-8 -*-

import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()
    setuptools.setup(
        name             = 'kagami',
        version          = '2.0.0',
        author           = 'Albert Zhou',
        author_email     = 'j.zhou.3@bham.ac.uk',
        url              = 'https://github.com/albert500/Kagami',
        packages         = setuptools.find_packages(),
        description      = 'The Kagami library',
        long_description = long_description,
        long_description_content_type = 'text/markdown',
        classifiers = [
            'Programming Language :: Python :: 2',
            'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
            'Operating System :: OS Independent',
        ],
    )
