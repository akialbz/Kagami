#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
webPortal

author(s): Albert (aki) Zhou
added: Jun. 28, 2014

"""


import logging, requests
from time import sleep
from typing import Any, Mapping, Optional
from kagami.comm import optional, available, partial


__all__ = ['get', 'post']


def _request(req, wait, tries, manual):
    def _conn(ti):
        try:
            resp = req()
            if resp.ok: return resp.text
            logging.warning('[%d] attempt connection failed: [%d] %s', ti, resp.status_code, resp.reason)
        except Exception as e:
            logging.warning('[%d] attempt connection failed: %s', ti, str(e))
        if ti > 0 and wait > 0: sleep(wait)
        return None

    res = None
    while True:
        for i in range(tries)[::-1]:
            res = _conn(i)
            if available(res): break
        if available(res) or not manual: break
        if input('\n[press any key to retry connection, or press "q" to quit] >> \n').strip().lower() == 'q': break
    return res


def get(url: str, *, params: Optional[Mapping] = None, headers: Optional[Mapping] = None,
        timeout: float = 3.05, wait: float = 1, tries: int = 1, manual: bool = False, **kwargs: Any) -> Optional[str]:
    req = partial(requests.get, url, params = optional(params, None), headers = optional(headers, None), timeout = timeout, **kwargs)
    return _request(req, wait, tries, manual)

def post(url: str, *, data: Optional[Mapping] = None, headers: Optional[Mapping] = None,
         timeout: float = 3.05, wait: float = 1, tries: int = 1, manual: bool = False, **kwargs: Any) -> Optional[str]:
    req = partial(requests.post, url, data = optional(data, None), headers = optional(headers, None), timeout = timeout, **kwargs)
    return _request(req, wait, tries, manual)
