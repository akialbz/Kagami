#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
model: machine learning model base class

author(s): Albert (aki) Zhou
origin: 08-18-2017

"""


class MLModel(object):
    _trained = False

    @property
    def trained(self):
        return self._trained

    @trained.setter
    def trained(self, value):
        self._trained = bool(value)

    def _checkTraining(self):
        if not self.trained: raise RuntimeError('model [%s] must be trained before use' % self.__class__.__name__)



