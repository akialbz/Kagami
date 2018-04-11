#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
classifier: data classifiers

author(s): Albert (aki) Zhou
origin: 09-22-2013

"""


import numpy as np
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import LinearSVC, SVC
from sklearn.naive_bayes import GaussianNB
from sklearn.neural_network import MLPClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, BaggingClassifier, AdaBoostClassifier
from ..prelim import NA, optional, hasvalue
from model import MLModel


class Classifier(MLModel):
    def __init__(self, method, **kwargs):
        clsdct = {
            'knnc':  KNeighborsClassifier,
            'lsvc':  LinearSVC,
            'rsvc':  SVC,
            'gaunb': GaussianNB,
            'mlpc':  MLPClassifier,
            'dtree': DecisionTreeClassifier,
            'randf': RandomForestClassifier,
            'bagg':  BaggingClassifier,
            'boost': AdaBoostClassifier,
        }
        if not clsdct.has_key(method): raise ValueError('unknown classifier [%s]' % method)
        self._cls = clsdct[method](**kwargs)

    def fit(self, ds, y):
        self._cls.fit(ds.values, y)
        self.trained = True
        return self

    def apply(self, ds):
        self._checkTraining()
        return self._cls.predict(ds.values)


class EnsembleClassifier(MLModel):
    def __init__(self, method, selectMatx, weights = NA, **kwargs):
        clsdct = {
            'knnc':  KNeighborsClassifier,
            'lsvc':  LinearSVC,
            'rsvc':  SVC,
            'gaunb': GaussianNB,
            'dtree': DecisionTreeClassifier,
        } # simple models only
        if not clsdct.has_key(method): raise ValueError('unknown classifier [%s]' % method)
        self._clss = [clsdct[method](**kwargs) for _ in selectMatx]

        if hasvalue(weights) and selectMatx.shape[0] != weights.shape[0]:
            raise ValueError('selection matrix and weights dimension not match')
        self._smtx = np.array(selectMatx, dtype = bool)
        self._w = optional(weights, np.ones(self._smtx.shape[0]))

    def fit(self, ds, y):
        self._clss = [c.fit(ds.values[:,np.where(s)],y) for c,s in zip(self._clss, self._smtx)]
        self.trained = True
        return self

    def apply(self, ds):
        self._checkTraining()
        pys = np.array([c.predict(ds.values[:,np.where(s)]) for c,s in zip(self._clss, self._smtx)])
        return np.round(np.average(pys, axis = 0, weights = self._w)).astype(int)
