#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
glm: general linear models

author(s): Albert (aki) Zhou
origin: 09-04-2017

"""


import numpy as np
from sklearn.linear_model import LinearRegression, Lasso, LassoCV, Ridge, RidgeCV, ElasticNet, ElasticNetCV
from model import MLModel


class GLMRegressor(MLModel):
    def __init__(self, method, cvTraining = False, **kwargs):
        regdct = {
            'lr':    LinearRegression,
            'lasso': (LassoCV if cvTraining else Lasso),
            'ridge': (RidgeCV if cvTraining else Ridge),
            'enet':  (ElasticNetCV if cvTraining else ElasticNet),
        }
        if not regdct.has_key(method): raise ValueError('unknown GLM regressor [%s]' % method)
        self._reg = regdct[method](**kwargs)

    @property
    def intercept(self):
        return self._reg.intercept_

    @property
    def coef(self):
        return self._reg.coef_

    def fit(self, ds, y):
        self._reg.fit(ds.values, y)
        self.trained = True
        return self

    def apply(self, ds):
        self._checkTraining()
        return self._reg.predict(ds.values)


class GLMSelector(MLModel):
    def __init__(self, method, cvTraining = False, cutoff = 0, **kwargs):
        self._glm = GLMRegressor(method = method, cvTraining = cvTraining, **kwargs)
        self._cut = cutoff

    @property
    def intercept(self):
        return self._glm.intercept

    @property
    def coef(self):
        return self._glm.coef

    @property
    def weights(self):
        cm = np.abs(self._glm.coef)
        return cm / float(np.sum(cm))

    @property
    def selected(self):
        return np.where(self.weights > self._cut)[0]

    def fit(self, ds, y):
        self._glm.fit(ds, y)
        self.trained = True
        return self

    def apply(self, ds):
        self._checkTraining()
        return ds[:,self.selected]
