#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
webPortal: portals to access basic web service

author(s): Albert (aki) Zhou
origin: Jun. 28, 2014

"""


import logging, requests, json
from time import sleep
from ..prelim import NA, optional
from ..functional import partial, iterate


def _request(req, wait, tries, manualRetry):
    def _conn(i):
        try:
            resp = req()
            if resp.ok: return resp.text
            logging.warning('[%d] attempt connection failed: [%d] %s' % (i, resp.status_code, resp.reason))
        except Exception, e:
            logging.warning('[%d] attempt connection failed: %s' % (i, str(e)))
        if i > 0 and wait > 0: sleep(wait)
        return None

    while True:
        res = iterate(range(tries)[::-1], _conn, lambda x: x is not None)
        if res is not None or not manualRetry: break
        if raw_input('\n[press any key to retry connection, or press "q" to quit] >> \n').strip().lower() == 'q': break

    if res is None: return None
    try: return json.loads(res)
    except ValueError: return res.strip()

def getUrl(url, params = NA, headers = NA, timeout = 3.05, wait = 1, tries = 1, manualRetry = False, **kwargs):
    req = partial(requests.get, url, params = optional(params, None), headers = optional(headers, None), timeout = timeout, **kwargs)
    return _request(req, wait, tries, manualRetry)

def postUrl(url, data = NA, headers = NA, timeout = 3.05, wait = 1, tries = 1, manualRetry = False, **kwargs):
    req = partial(requests.post, url, data = optional(data, None), headers = optional(headers, None), timeout = timeout, **kwargs)
    return _request(req, wait, tries, manualRetry)
