#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
test_webPortal

author(s): Albert (aki) Zhou
added: 11-22-2018

"""


import pytest, json
from urllib.request import urlopen
from urllib.error import URLError
from kagami.comm import *
from kagami.portals import webPortal


def _connected():
    try: urlopen('https://httpbin.org/', timeout = 1); return True
    except URLError: return False

@pytest.mark.skipif(not _connected(), reason = 'no connection to internet')
def test_get_io():
    ret = json.loads(webPortal.get('https://httpbin.org/get', params = {'b': 'bb'}, headers = {'a': 'aa'}))
    assert ret['args'] == {'b': 'bb'}
    assert ret['headers']['A'] == 'aa' and ret['headers']['Host'] == 'httpbin.org'
    assert ret['url'] == 'https://httpbin.org/get?b=bb'

    ret = webPortal.get('https://httpbin.org/no-such-website', tries = 3)
    assert missing(ret)

    ret = webPortal.get('http://no-such-website.com', tries = 3)
    assert missing(ret)

@pytest.mark.skipif(not _connected(), reason = 'no connection to internet')
def test_post_io():
    ret = json.loads(webPortal.post('https://httpbin.org/post', params = {'b': 'bb'}, headers = {'a': 'aa'}))
    assert ret['args'] == {'b': 'bb'}
    assert ret['headers']['A'] == 'aa' and ret['headers']['Host'] == 'httpbin.org'
    assert ret['url'] == 'https://httpbin.org/post?b=bb'

    ret = webPortal.post('https://httpbin.org/no-such-website', tries = 3)
    assert missing(ret)

    ret = webPortal.post('http://no-such-website.com', tries = 3)
    assert missing(ret)
