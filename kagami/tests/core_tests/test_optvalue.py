#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
test_core.py

author(s): Albert (aki) Zhou
origin: 11-14-2018

"""


import cPickle as cp
import numpy as np
from copy import deepcopy
from kagami.core import *


def test_na():
    assert na == na and na == deepcopy(na)
    assert na != '' and na is not None
    assert isinstance(na, NAType)

    assert na.char_ == str(na) == ''
    assert na.integer_ == int(na) == -9223372036854775808
    assert np.isnan(na.float_) and np.isnan(float(na))
    assert na.bool_ == bool(na) == False

    assert repr(na) == 'N/A'

    assert cp.loads(cp.dumps(na)) == na
    assert na.copy() == na

    assert missing(na) and not missing(None)
    assert available('') and available(False) and available(np.nan) and available(())
    assert optional('a', 'b') == 'a' and optional(None, 'b') is None and optional(na, 'b') == 'b'

    assert isnull(na) and isnull(None)
    assert not (isnull('') or isnull(False) or isnull(np.nan) or isnull(()))

    assert isna(na)
    assert not isna('') and not isna(None)

    assert np.all(isna(np.array([1,  2,  na.integer_,  3,  na.integer_, 3 ], dtype = int)) ==
                       np.array([0,  0,  1,            0,  1,           0 ], dtype = bool))
    assert np.all(isna(np.array([1., 2., np.nan,       3., np.nan,      3.], dtype = float)) ==
                       np.array([0,  0,  1,            0,  1,           0 ], dtype = bool))
    assert np.all(isna(np.array([1., na, float('nan'), 3., np.nan,      3 ], dtype = object)) ==
                       np.array([0,  1,  1,            0,  1,           0 ], dtype = bool))

    assert np.all(isna([1.,    na,   float('nan'), 3.,    np.nan, na.integer_, 3,     False, '']) ==
                       [False, True, True,         False, True,   True,        False, False, False])

