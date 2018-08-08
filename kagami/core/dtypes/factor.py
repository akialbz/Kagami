#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
factor

author(s): Albert (aki) Zhou
origin: 08-08-2018

"""


from collections import OrderedDict
from kagami.core.prelim import NA, optional


class factor(object):
    def __init__(self, values = NA):
        self._fdct = OrderedDict()
        for i,v in enumerate(optional(values, ())):
            if self._fdct.has_key(v): continue
            self._fdct[v] = i

    # build-ins
    def __len__(self):
        return len(self._fdct)

    # properties
    @property
    def levels(self):
        return self._fdct.keys()

    @property
    def values(self):
        return self._fdct.values()

    # methods
    def levelof(self, value):
        return self._fdct.keys()[value]

    def valueof(self, level):
        return self._fdct[level]


