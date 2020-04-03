#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
coreType

author(s): Albert (aki) Zhou
added: 08-23-2018

"""


import pickle
import numpy as np
from typing import Tuple, Sequence, Union, Optional
from copy import deepcopy
from kagami.comm import pickmap


__all__ = ['CoreType', 'Indices', 'Indices2D']


Indices = Union[int, str, Sequence[Union[int, str]], slice, None]
Indices2D = Union[Indices, Tuple[Indices], Tuple[Indices, Optional[Indices]]]


class CoreType:
    __slots__ = ()

    # built-ins
    def __getitem__(self, item):
        raise NotImplementedError(f'method not implemented for {self.__class__.__name__}')

    def __setitem__(self, key, value):
        raise NotImplementedError(f'method not implemented for {self.__class__.__name__}')

    def __delitem__(self, key):
        raise NotImplementedError(f'method not implemented for {self.__class__.__name__}')

    def __iter__(self):
        raise NotImplementedError(f'method not implemented for {self.__class__.__name__}')

    def __contains__(self, item):
        raise NotImplementedError(f'method not implemented for {self.__class__.__name__}')

    def __len__(self):
        raise NotImplementedError(f'method not implemented for {self.__class__.__name__}')

    def __eq__(self, other):
        raise NotImplementedError(f'method not implemented for {self.__class__.__name__}')

    def __ne__(self, other):
        return np.logical_not(self.__eq__(other))

    def __add__(self, other):
        return self.append(other, inline = False)

    def __iadd__(self, other):
        return self.append(other, inline = True)

    def __str__(self):
        raise NotImplementedError(f'method not implemented for {self.__class__.__name__}')

    def __repr__(self):
        raise NotImplementedError(f'method not implemented for {self.__class__.__name__}')

    # for numpy
    def __array__(self, dtype = None):
        raise NotImplementedError(f'method not implemented for {self.__class__.__name__}')

    def __array_wrap__(self, arr):
        raise NotImplementedError(f'method not implemented for {self.__class__.__name__}')

    # for pickle
    def __getstate__(self):
        return {k: getattr(self, k) for k in self.__slots__}

    def __setstate__(self, dct):
        pickmap(dct.keys(), lambda x: x in self.__slots__, lambda x: setattr(self, x, dct[x]))

    # properties
    @property
    def size(self):
        raise NotImplementedError(f'method not implemented for {self.__class__.__name__}')

    @property
    def shape(self):
        raise NotImplementedError(f'method not implemented for {self.__class__.__name__}')

    @property
    def ndim(self):
        raise NotImplementedError(f'method not implemented for {self.__class__.__name__}')

    # public
    def take(self, pos):
        raise NotImplementedError(f'method not implemented for {self.__class__.__name__}')

    def put(self, pos, value, inline = False):
        raise NotImplementedError(f'method not implemented for {self.__class__.__name__}')

    def append(self, value, inline = False):
        raise NotImplementedError(f'method not implemented for {self.__class__.__name__}')

    def insert(self, pos, value, inline = False):
        raise NotImplementedError(f'method not implemented for {self.__class__.__name__}')

    def delete(self, pos, inline = False):
        raise NotImplementedError(f'method not implemented for {self.__class__.__name__}')

    def tolist(self):
        raise NotImplementedError(f'method not implemented for {self.__class__.__name__}')

    def tostring(self):
        raise NotImplementedError(f'method not implemented for {self.__class__.__name__}')

    def dump(self, file, protocol = None) -> None:
        return pickle.dump(self, file = file, protocol = protocol)

    def dumps(self, protocol = None) -> bytes:
        return pickle.dumps(self, protocol = protocol)

    def copy(self):
        return deepcopy(self)
