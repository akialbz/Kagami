#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
resampler: dataset re-sampler

author(s): Albert (aki) Zhou
origin: 01-09-2018

"""


import numpy as np
from itertools import cycle
from ..prelim import NA, optional
from model import MLModel


class Bootstrap(MLModel):
    def __init__(self, fold = 10, runs = 1, shuffle = True):
        self._shuffle = shuffle
        self._fold = fold
        self._runs = runs
        self._dss = NA
        self._fids = NA

    def fit(self, *dss):
        self._dss = list(dss)
        lens = map(len, self._dss)
        maxl = max(lens)

        def _cv():
            lids = [(np.random.permutation(l) if self._shuffle else np.arange(l)) for l in lens]
            fblk = np.array_split(np.array(zip(*map(lambda x: x if len(x) == maxl else cycle(x), lids))).T, self._fold, axis = 1)
            return [(np.hstack(fblk[:i] + fblk[i+1:]), fblk[i]) for i in range(self._fold)]
        self._fids = reduce(lambda x,y: x+y, [_cv() for _ in range(self._runs)])

        self.trained = True
        return self

    def apply(self):
        self._checkTraining()
        for tids, vids in self._fids: yield [(d[list(ti),], d[list(vi),]) for ti,vi,d in zip(tids, vids, self._dss)]


class LabelBootstrap(MLModel):
    def __init__(self, fold = 10, runs = 1, shuffle = True):
        self._shuffle = shuffle
        self._fold = fold
        self._runs = runs
        self._dss = NA
        self._fids = NA
        self._ndmx = NA

    def _getds(self, ids, ds):
        inds = map(lambda x: x in ds.rownames, ids)
        ndm = np.delete(self._ndmx, np.where(inds)[0], axis = 1)
        nid = np.delete(ids, np.where(inds)[0])
        return ds[[(i if n else np.random.choice(nid[d == np.min(d)])) for i,n,d in zip(ids,inds,ndm)],]

    def fit(self, ndmatx = NA, *dss):
        self._dss = list(dss)
        unams = list(set.union(*map(lambda x: getattr(x, 'rownames'), self._dss)))

        def _cv():
            if self._shuffle: np.random.shuffle(unams)
            fblk = np.array_split(unams, self._fold)
            return [(np.hstack(fblk[:i] + fblk[i+1:]), fblk[i]) for i in range(self._fold)]
        self._fids = reduce(lambda x,y: x+y, [_cv() for _ in range(self._runs)])

        self._ndmx = optional(ndmatx, np.ones((len(unams),len(unams))))
        self.trained = True
        return self

    def apply(self):
        self._checkTraining()
        for tids, vids in self._fids: yield [(self._getds(tids, d), self._getds(vids, d)) for d in self._dss]

