#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
test_dtypes_coreType

author(s): Albert (aki) Zhou
origin: 10-01-2018

"""


import pytest
import numpy as np
from kagami.dtypes import CoreType


def test_coretype_creation():
    cobj = CoreType()
    cobj = cobj.copy()

def test_coretype_built_ins():
    cobj = CoreType()
    with pytest.raises(NotImplementedError): cobj[0]
    with pytest.raises(NotImplementedError): cobj[0] = 1
    with pytest.raises(NotImplementedError): del cobj[0]
    with pytest.raises(NotImplementedError): [v for v in cobj]
    with pytest.raises(NotImplementedError): 1 in cobj
    with pytest.raises(NotImplementedError): 1 not in cobj
    with pytest.raises(NotImplementedError): len(cobj)
    with pytest.raises(NotImplementedError): cobj == 1
    with pytest.raises(NotImplementedError): cobj += 1
    with pytest.raises(NotImplementedError): str(cobj)
    with pytest.raises(NotImplementedError): repr(cobj)
    with pytest.raises(NotImplementedError): np.array(cobj)

def test_coretype_properties():
    cobj = CoreType()
    with pytest.raises(NotImplementedError): cobj.size
    with pytest.raises(NotImplementedError): cobj.shape
    with pytest.raises(NotImplementedError): cobj.ndim

def test_coretype_methods():
    cobj = CoreType()
    with pytest.raises(NotImplementedError): cobj.append(1)
    with pytest.raises(NotImplementedError): cobj.insert(1)
    with pytest.raises(NotImplementedError): cobj.drop(1)
