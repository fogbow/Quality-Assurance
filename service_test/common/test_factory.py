# -*- coding: utf-8 -*-

import json
import requests

from collections import namedtuple
from os import path
from . import HttpMethods

__all__ = ['TestEngine']

class TestEngine(object):
    def __init__(self, service_url):
        self.last_create = None
        self.service_url = service_url;
        self.body = {}
        self.headers = {}

    def wait_until_ready(self, tries = -1):
        if tries == 0:
            return None
        lasturl = str(self.last_create.url)
        last_create = json.loads(self.last_create)
        instance_id = last_create['id']
        url = lasturl + '/' + instance_id
        response_json = requests.get(url=url, headers=headers).json()
        response = json.loads(response_json)

        if response['state'] == InstanceState.READY:
            ret = response
        else:
            ret = self.wait_until_ready(tries-1)

        return ret

    def create(self, resource, **kwargs):
        available_endpoints = {
            'token': '/tokens'
        }

        urlpath = available_endpoints[resource]
        url = self.service_url + '/' + urlpath

        headers = kwargs.get('headers', self.headers)
        body    = kwargs.get('body', self.body)

        req = FogbowRequest(url=url, headers=headers, body=body, method=str(HttpMethods.POST))
        self.last_create = req.execute()

        return self.last_create

    def addHeader(self, header, headervalue):
        self.headers[header] = headervalue

class FogbowRequest:
    def __init__(self, url, method = 'get', body = {}, headers = {}):
        self.url = url
        self.headers = headers
        self.body = body
        self.method = method

    def execute(self):
        verb_requester = getattr(requests, self.method)
        return verb_requester(url=self.url, json=self.body, headers=self.headers)
