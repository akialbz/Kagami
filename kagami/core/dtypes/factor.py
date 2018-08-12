#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
factor

author(s): Albert (aki) Zhou
origin: 08-08-2018

"""


import logging
import numpy as np
from bidict import OrderedBidict, FrozenOrderedBidict
from kagami.core.prelim import NA, hasvalue, isna, checkany, hashable
from kagami.core.functional import partial


class Factor(object):
    __slots__ = ('_array', '_levdct', '_valbase')
    def __init__(self, array, levels = NA, values = NA, mutable = False):
        if hasvalue(levels) and checkany(array, lambda x: x not in levels): raise ValueError('value(s) not in levels')
        if hasvalue(levels) and len(levels) != len(set(levels)): raise ValueError('levels have duplications')
        if hasvalue(levels) and checkany(levels, lambda x: not hashable(x)): raise TypeError('levels not hashable')
        if hasvalue(values) and len(values) != len(set(values)): raise ValueError('values have duplications')
        if hashable(values) and checkany(values, lambda x: not isinstance(x, int)): raise TypeError('values are not integers')
        if hasvalue(levels) and hasvalue(values) and len(levels) != len(values): raise ValueError('levels and values size not match')
        if hasvalue(values) and isna(levels): logging.warning('levels not given, ignore level value assignment')

        if isna(levels): levels = list(set(array))
        if isna(values): values = range(len(levels))
        if len(levels) == 0: raise ValueError('no level assigned')

        self._levdct = (OrderedBidict if mutable else FrozenOrderedBidict)(sorted(zip(levels, values), key = lambda x: x[1]))
        self._array = np.array([self._levdct[v] for v in array])
        self._valbase = np.min(self._array)
        


#
    #
    #
    # fct = type(name, (object,), {'__slots__': tuple(levels) + ('_valdct', 'nlevels', 'levels', 'values', 'items', 'encode', 'decode')})
    #
    # # privates
    #
    #
    # # build-ins
    # fct.__len__ = lambda self: len(self._valdct)
    #
    # # properties
    # def _getter(self, lev):
    #     return self
    # def _setter(self, val, lev):
    #     self._valdct[lev] = val
    # for l in levels: setattr(fct, l, property(partial(_getter, lev = l), partial(_setter, lev = l)))
    #
    # fct.nlevels = property(lambda self: len(self._valdct))
    # fct.levels = property(lambda self: self._valdct.keys())
    # fct.values = property(lambda self: self._valdct.values())
    # fct.items = property(lambda self: self._valdct.items())
    #
    # # methods
    # fct.encode = classmethod(lambda cls, val: [cls._valdct[v] for v in val])
    # fct.decode = classmethod(lambda cls, val: [cls._valdct.inv[v] for v in val])
    #
    # return fct
    #

if __name__ == '__main__':
    Color = factor('Colors', ('r', 'g', 'b'), mutable =  True)
    xx = [Color.r, Color.g, Color.b]
    import pdb; pdb.set_trace()


