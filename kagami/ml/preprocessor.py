#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
preprocessor: data preprocessors

author(s): Albert (aki) Zhou
origin: 12-27-2017

"""


import numpy as np
from sklearn.preprocessing import Imputer
from sklearn.preprocessing import StandardScaler, Normalizer
from fancyimpute import KNN
from scipy.stats import iqr
from ..prelim import NA, optional, isna
from ..functional import lassign
from model import MLModel


class NullFilter(MLModel):
    def __init__(self, cutoff = 0.5, nullValue = np.nan):
        if not 0 < cutoff <= 1: raise ValueError('null filter curoff not in range (0, 1]')
        self._cutoff = cutoff
        self._isnull = (lambda x: np.isnan(x)) if np.isnan(nullValue) else \
                       (lambda x: np.isclose(x, nullValue)) if isinstance(nullValue, float) else \
                       (lambda x: x == nullValue)
        self._retids = NA

    def _fit(self, ds, axis):
        return np.where(np.sum(self._isnull(ds.values), axis = axis) <= np.round(self._cutoff * ds.shape[axis]))[0]

    def fit(self, ds, axis = 0):
        self._retids = self._fit(ds, axis)
        return self

    def apply(self, ds, axis = 0):
        rids = optional(self._retids, self._fit(ds, axis))
        return ds[rids,] if axis == 0 else ds[:,rids]


class NullImputer(MLModel):
    def __init__(self, method = 'mean', nullValue = np.nan, fillValue = 0, **kwargs):
        self._method = method
        self._isnull = (lambda x: np.isnan(x)) if np.isnan(nullValue) else \
                       (lambda x: np.isclose(x, nullValue)) if isinstance(nullValue, float) else \
                       (lambda x: x == nullValue)
        self._filval = fillValue
        self._params = kwargs
        self._impute = NA

    def fit(self, ds, axis = 0):
        if self._method not in ('fill', 'knn'):
            self._impute = Imputer(strategy = self._method, axis = axis, **self._params).fit(ds.values)
            self.trained = True
        return self

    def apply(self, ds, axis = 0):
        if self._method not in ('fill', 'knn'): self._checkTraining()
        dm = ds.values.astype(float) # and copy
        dm[self._isnull] = np.nan
        nds = ds.copy()
        nds.values = lassign(dm, index = np.isnan(dm), value = self._filval) if self._method == 'fill' else \
                     KNN(orientation = ('rows', 'columns')[axis], **self._params).complete(dm) if self._method == 'knn' else \
                     self._impute.transform(dm)
        return nds


class Scaler(MLModel): # on feature
    def __init__(self, mean = True, std = True):
        self._scaler = StandardScaler(with_mean = mean, with_std = std)

    def fit(self, ds):
        self._scaler.fit(ds.values)
        self.trained = True
        return self

    def apply(self, ds):
        self._checkTraining()
        nds = ds.copy()
        nds.values = self._scaler.transform(nds.values)
        return nds


class Normaliser(MLModel): # on sample
    def __init__(self, norm = 'l2'):
        self._norm = Normalizer(norm = norm)

    def fit(self, ds):
        self._norm.fit(ds.values)
        self.trained = True
        return self

    def apply(self, ds):
        self._checkTraining()
        nds = ds.copy()
        nds.values = self._norm.transform(nds.values)
        return nds


class QuantileFilter(MLModel):
    def __init__(self, cutoff = 0.8):
        if not 0.5 < cutoff < 1: raise ValueError('quantile filter curoff not in range (0.5, 1)')
        self._cutoff = cutoff
        self._retids = NA

    def _fit(self, ds, axis):
        lbd = np.percentile(ds.values, int((1 - self._cutoff) * 100))
        ubd = np.percentile(ds.values, int(self._cutoff * 100))
        return np.where(np.sum(np.logical_and(lbd < ds.values, ds.values < ubd), axis = axis) == 0)[0]

    def fit(self, ds, axis = 0):
        self._retids = self._fit(ds, axis)
        return self

    def apply(self, ds, axis = 0):
        rids = optional(self._retids, self._fit(ds, axis))
        return ds[rids,] if axis == 0 else ds[:,rids]


class VarianceFilter(MLModel):
    def __init__(self, method = 'iqr', cutoff = 0.5, quantile = True):
        if quantile and not 0 < cutoff < 1: raise ValueError('variance filter curoff not in range (0, 1)')
        self._var = {'iqr': iqr, 'var': np.var, 'std': np.std}.get(method, NA)
        if isna(self._var): raise ValueError('unknow variance function [%s]' % method)
        self._cutoff = cutoff
        self._quanti = quantile
        self._retids = NA

    def _fit(self, ds, axis):
        varval = self._var(ds.values, axis = axis)
        cutoff = self._cutoff if not self._quanti else \
                 np.sort(varval)[int(np.round(ds.shape[axis] * self._cutoff))]
        return np.where(varval >= cutoff)[0]

    def fit(self, ds, axis = 0):
        self._retids = self._fit(ds, axis)
        return self

    def apply(self, ds, axis = 0):
        rids = optional(self._retids, self._fit(ds, axis))
        return ds[rids,] if axis == 0 else ds[:,rids]
