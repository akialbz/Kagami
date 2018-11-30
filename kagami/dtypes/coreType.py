#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
coreType

author(s): Albert (aki) Zhou
origin: 08-23-2018

"""


import numpy as np
from copy import deepcopy
from kagami.core import na, pickmap


__all__ = ['CoreType']


class CoreType(object):
    __slots__ = ()

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

    def __len__(self):
        raise NotImplementedError('method not implemented for Kagami CoreType')

    def __eq__(self, other):
        raise NotImplementedError('method not implemented for Kagami CoreType')

    def __ne__(self, other):
        return np.logical_not(self.__eq__(other))

    def __add__(self, other):
        return self.append(other)

    def __iadd__(self, other):
        raise NotImplementedError('method not implemented for Kagami CoreType')

    def __str__(self):
        raise NotImplementedError('method not implemented for Kagami CoreType')

    def __repr__(self):
        raise NotImplementedError('method not implemented for Kagami CoreType')

    # for numpy
    def __array__(self, dtype = None):
        raise NotImplementedError('method not implemented for Kagami CoreType')

    # for pickle
    def __getstate__(self):
        return {k: getattr(self, k) for k in self.__slots__}

    def __setstate__(self, dct):
        pickmap(dct.keys(), lambda x: x in self.__slots__, lambda x: setattr(self, x, dct[x]))

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

    def insert(self, other, pos = na):
        raise NotImplementedError('method not implemented for Kagami CoreType')

    def drop(self, pos):
        raise NotImplementedError('method not implemented for Kagami CoreType')

    def copy(self):
        return deepcopy(self)

