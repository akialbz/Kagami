#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
metadata

author(s): Albert (aki) Zhou
origin: 06-07-2016

"""


__all__ = ['Metadata']


# metadata type
class Metadata(dict):
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        super(Metadata, self).__init__(*args, **kwargs)

    def __getattr__(self, item):
        return self[item] if self.has_key(item) else super(Metadata, self).__getattribute__(item)

    def __setattr__(self, item, value):
        if item not in self.__slots__: self[item] = value
        else: super(Metadata, self).__setattr__(item, value)

    def __delattr__(self, item):
        if self.has_key(item): del self[item]
        else: super(Metadata, self).__delattr__(item)

    def __getstate__(self):
        return {k: getattr(self, k) for k in self.__slots__}

    def __setstate__(self, dct):
        for k in filter(lambda x: x in self.__slots__, dct.keys()): setattr(self, k, dct[k])

