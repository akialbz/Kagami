#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
webPortal

author(s): Albert (aki) Zhou
origin: Jun. 28, 2014

"""


import logging, requests, json
from time import sleep
from kagami.core import na, optional, available, missing, partial


def _request(req, wait, tries, manualRetry):
    def _conn(ti):
        try:
            resp = req()
            if resp.ok: return resp.text
            logging.warning('[%d] attempt connection failed: [%d] %s' % (ti, resp.status_code, resp.reason))
        except Exception, e:
            logging.warning('[%d] attempt connection failed: %s' % (ti, str(e)))
        if ti > 0 and wait > 0: sleep(wait)
        return na

    tries = max(tries, 1)
    while True:
        for i in range(tries)[::-1]:
            res = _conn(i)
            if available(res): break
        if available(res) or not manualRetry: break
        if raw_input('\n[press any key to retry connection, or press "q" to quit] >> \n').strip().lower() == 'q': break

    if missing(res): return na
    if res is None: return None
    try: return json.loads(res)
    except ValueError: return res.strip()


def get(url, params = na, headers = na, timeout = 3.05, wait = 1, tries = 1, manualRetry = False, **kwargs):
    logging.debug('getting url [%s]' % url)
    req = partial(requests.get, url, params = optional(params, None), headers = optional(headers, None), timeout = timeout, **kwargs)
    return _request(req, wait, tries, manualRetry)

def post(url, data = na, headers = na, timeout = 3.05, wait = 1, tries = 1, manualRetry = False, **kwargs):
    logging.debug('posting url [%s]' % url)
    req = partial(requests.post, url, data = optional(data, None), headers = optional(headers, None), timeout = timeout, **kwargs)
    return _request(req, wait, tries, manualRetry)
