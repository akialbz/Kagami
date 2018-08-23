#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
coreType

author(s): Albert (aki) Zhou
origin: 08-23-2018

"""


from copy import deepcopy
from kagami.core import NA


class CoreType(object):
    # built-ins
    def __getitem__(self, item):
        raise NotImplementedError('method not implemented for Kagami CoreType')

    def __setitem__(self, key, value):
        raise NotImplementedError('method not implemented for Kagami CoreType')

    def __delitem__(self, key):
        raise NotImplementedError('method not implemented for Kagami CoreType')

    def __iter__(self):
        raise NotImplementedError('method not implemented for Kagami CoreType')

    def __contains__(self, item):
        raise NotImplementedError('method not implemented for Kagami CoreType')

    def __eq__(self, other):
        raise NotImplementedError('method not implemented for Kagami CoreType')

    def __len__(self):
        raise NotImplementedError('method not implemented for Kagami CoreType')

    def __str__(self):
        raise NotImplementedError('method not implemented for Kagami CoreType')

    def __repr__(self):
        raise NotImplementedError('method not implemented for Kagami CoreType')

    # properties
    @property
    def size(self):
        raise NotImplementedError('method not implemented for Kagami CoreType')

    @property
    def shape(self):
        raise NotImplementedError('method not implemented for Kagami CoreType')

    @property
    def ndim(self):
        raise NotImplementedError('method not implemented for Kagami CoreType')

    # public
    def append(self, other):
        raise NotImplementedError('method not implemented for Kagami CoreType')

    def insert(self, other, pos = NA):
        raise NotImplementedError('method not implemented for Kagami CoreType')

    def drop(self, pos):
        raise NotImplementedError('method not implemented for Kagami CoreType')

    def copy(self):
        return deepcopy(self)

