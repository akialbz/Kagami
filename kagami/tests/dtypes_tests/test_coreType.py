#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
test_dtypes_coreType

author(s): Albert (aki) Zhou
added: 10-01-2018

"""


import os, pytest, pickle as pkl
import numpy as np
from kagami.dtypes import CoreType


def test_coretype_creation():
    cobj = CoreType()
    _ = cobj.copy()

def test_coretype_built_ins():
    cobj = CoreType()
    with pytest.raises(NotImplementedError): _ = cobj[0]
    with pytest.raises(NotImplementedError): cobj[0] = 1
    with pytest.raises(NotImplementedError): del cobj[0]
    with pytest.raises(NotImplementedError): _ = [v for v in cobj]
    with pytest.raises(NotImplementedError): _ = 1 in cobj
    with pytest.raises(NotImplementedError): _ = 1 not in cobj
    with pytest.raises(NotImplementedError): len(cobj)
    with pytest.raises(NotImplementedError): _ = cobj == 1
    with pytest.raises(NotImplementedError): cobj += 1
    with pytest.raises(NotImplementedError): str(cobj)
    with pytest.raises(NotImplementedError): repr(cobj)
    with pytest.raises(NotImplementedError): np.array(cobj)

def test_coretype_properties():
    cobj = CoreType()
    with pytest.raises(NotImplementedError): _ = cobj.size
    with pytest.raises(NotImplementedError): _ = cobj.shape
    with pytest.raises(NotImplementedError): _ = cobj.ndim

def test_coretype_methods():
    cobj = CoreType()
    with pytest.raises(NotImplementedError): cobj.take(1)
    with pytest.raises(NotImplementedError): cobj.put(1, None)
    with pytest.raises(NotImplementedError): cobj.append(None)
    with pytest.raises(NotImplementedError): cobj.insert(1, None)
    with pytest.raises(NotImplementedError): cobj.delete(1)
    with pytest.raises(NotImplementedError): cobj.tolist()
    with pytest.raises(NotImplementedError): cobj.tostring()

def test_coretype_dumps():
    cobj = CoreType()
    assert pkl.loads(cobj.dumps()).__class__ == CoreType

    fname = 'test_coreType_dump.pkl'
    with open(fname, 'wb') as f: cobj.dump(f)
    with open(fname, 'rb') as f: pkl.load(f)
    if os.path.isfile(fname): os.remove(fname)
