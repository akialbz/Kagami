#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
structArray

author(s): Albert (aki) Zhou
origin: 08-23-2018

"""


import numpy as np
from collections import OrderedDict
from kagami.core import NA, isna
from kagami.dtypes import NamedIndex


class StructuredArray(object):
    def __init__(self, valueNames = NA, fixedSize = NA, *args, **kwargs):
        self._adict = OrderedDict(*args, **kwargs)
        self._vnames = valueNames
        self._fxsize = fixedSize

        for k,v in self._adict.items():
            if isna(self._fxsize): self._fxsize = len(v)
            self._adict[k] = np.array()



        if hasvalue(seq):
            super(StructuredArray, self).__init__(seq)
        else:
            super(StructuredArray, self).__init__(**kwargs)

        if hasvalue(size):
            self._size = size
        elif len(self) > 0:
            self._size = len(self.values()[0])
        else:
            raise ValueError('must provide index size or initial values')

        for k,v in self.items(): self[k] = _packArray(v)

    # built-ins
    def __getitem__(self, item):
        if hashable(item) and self.has_key(item):
            value = super(_Index, self).__getitem__(item)
        else:
            _pack = lambda x: x.reshape((1,)) if x.ndim == 0 else x
            value = _Index([(k,_pack(v[item])) for k,v in self.items()])
        return value

    def __setitem__(self, key, value):
        if isinstance(value, _Index):
            if checkany(self.keys(), lambda x: not value.has_key(x)): raise KeyError('index has different keys')
            for k in self.keys():
                if self[k].dtype.kind == value[k].dtype.kind == 'S':
                    sdl, vdl = self[k].dtype.itemsize, value[k].dtype.itemsize
                    if sdl < vdl: self[k] = self[k].astype('S%d' % vdl)
                self[k][key] = value[k]
        else:
            value = _packArray(value)
            if len(value) != self._size: raise ValueError('index values size not match')
            super(_Index, self).__setitem__(key, value)

    def __add__(self, other):
        return self.insert(other)

    def __eq__(self, other):
        if len(self) != len(other) or set(self.keys()) != set(other.keys()) or \
           checkany(self.keys(), lambda x: np.any(self[x] != other[x])): return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    # properties
    @property
    def size(self):
        return self._size

    @property
    def shape(self):
        return len(self), self._size

    # publics
    @classmethod
    def stack(cls, idx1, idx2):
        if not isinstance(idx1, _Index) or not isinstance(idx2, _Index): raise TypeError('unknown index type(s)')
        return idx1.insert(idx2)

    def insert(self, other, pos = NA):
        if not isinstance(other, _Index): raise TypeError('insert object is not Index')
        if checkany(self.keys(), lambda x: not other.has_key(x)): raise KeyError('index has different keys')
        if isna(pos): pos = self._size
        return _Index([(k, np.insert(v, pos, other[k])) for k,v in self.items()])

    def drop(self, pos):
        return _Index([(k, np.delete(v, pos)) for k,v in self.items()])

    def toList(self, transpose = False):
        olst = [[k] + list(v) for k,v in self.items()]
        return olst if not transpose else list(map(list,zip(*olst)))

    def copy(self):
        return _Index(self.items(), size = self._size)

