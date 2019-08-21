#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
coreType

author(s): Albert (aki) Zhou
origin: 08-23-2018

"""


import pickle
import numpy as np
from copy import deepcopy
from kagami.common import pickmap


__all__ = ['CoreType']


class CoreType:
    __slots__ = ()

    # built-ins
    def __getitem__(self, item):
        raise NotImplementedError('method not implemented for CoreType')

    def __setitem__(self, key, value):
        raise NotImplementedError('method not implemented for CoreType')

    def __delitem__(self, key):
        raise NotImplementedError('method not implemented for CoreType')

    def __iter__(self):
        raise NotImplementedError('method not implemented for CoreType')

    def __contains__(self, item):
        raise NotImplementedError('method not implemented for CoreType')

    def __len__(self):
        raise NotImplementedError('method not implemented for CoreType')

    def __eq__(self, other):
        raise NotImplementedError('method not implemented for CoreType')

    def __ne__(self, other):
        return np.logical_not(self.__eq__(other))

    def __add__(self, other):
        return self.append(other)

    def __str__(self):
        raise NotImplementedError('method not implemented for CoreType')

    def __repr__(self):
        raise NotImplementedError('method not implemented for CoreType')

    # for numpy
    def __array__(self, dtype = None):
        raise NotImplementedError('method not implemented for CoreType')

    def __array_wrap__(self, arr):
        raise NotImplementedError('method not implemented for CoreType')

    # for pickle
    def __getstate__(self):
        return {k: getattr(self, k) for k in self.__slots__}

    def __setstate__(self, dct):
        pickmap(dct.keys(), lambda x: x in self.__slots__, lambda x: setattr(self, x, dct[x]))

    # properties
    @property
    def size(self):
        raise NotImplementedError('method not implemented for CoreType')

    @property
    def shape(self):
        raise NotImplementedError('method not implemented for CoreType')

    @property
    def ndim(self):
        raise NotImplementedError('method not implemented for CoreType')

    # public
    def take(self, pos):
        raise NotImplementedError('method not implemented for CoreType')

    def put(self, pos, value):
        raise NotImplementedError('method not implemented for CoreType')

    def append(self, value, inline = False):
        raise NotImplementedError('method not implemented for CoreType')

    def insert(self, pos, value, inline = False):
        raise NotImplementedError('method not implemented for CoreType')

    def delete(self, pos, inline = False):
        raise NotImplementedError('method not implemented for CoreType')

    def tolist(self):
        raise NotImplementedError('method not implemented for CoreType')

    def tostring(self):
        raise NotImplementedError('method not implemented for CoreType')

    def dump(self, file, protocol = None) -> None:
        return pickle.dump(self, file = file, protocol = protocol)

    def dumps(self, protocol = None) -> bytes:
        return pickle.dumps(self, protocol = protocol)

    def sort(self, kind = 'quicksort', inline = False):
        raise NotImplementedError('method not implemented for CoreType')

    def argsort(self, kind = 'quicksort'):
        raise NotImplementedError('method not implemented for CoreType')

    def copy(self):
        return deepcopy(self)
