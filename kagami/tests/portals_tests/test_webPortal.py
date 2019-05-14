#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
test_webPortal

author(s): Albert (aki) Zhou
origin: 11-22-2018

"""


import urllib2, pytest
from kagami.core import *
from kagami.portals import webPortal


def _connected():
    try: urllib2.urlopen('http://rest.kegg.jp', timeout = 1); return True
    except urllib2.URLError: return False

@pytest.mark.skipif(not _connected(), reason = 'no connection to KEGG rest APIs')
def test_get_io():
    ret = webPortal.get('http://rest.kegg.jp/link/ko/cge:113831488')
    assert ret == 'cge:113831488\tko:K19752'

    ret = webPortal.get('http://rest.kegg.jp/no-such-website', tries = 3)
    assert missing(ret)

    ret = webPortal.get('http://no-such-website.com', tries = 3)
    assert missing(ret)

@pytest.mark.skipif(not _connected(), reason = 'no connection to KEGG rest APIs')
def test_post_io():
    ret = webPortal.post('http://rest.kegg.jp/link/ko/cge:113831488')
    assert ret == 'cge:113831488\tko:K19752'

    ret = webPortal.post('http://rest.kegg.jp/no-such-website', tries = 3)
    assert missing(ret)

    ret = webPortal.post('http://no-such-website.com', tries = 3)
    assert missing(ret)
