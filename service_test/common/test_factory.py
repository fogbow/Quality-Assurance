# -*- coding: utf-8 -*-

import requests

from . import HttpMethods

class TestFactory(object):
    def __init__(self, service_url):
        self.test = TestInstance(url=url)

class RasInstance:
    def __init__(self, url):
        self.url = url
        self.headers = {}
        self.body = {}
        self.waits = []
        self.instanceid = None
        self.last
        self.method = HttpMethods.GET

    def addHeader(self, header, headervalue):
        self.headers[header] = headervalue
        return self

    def addBodyField(self, field, value):
        self.body[field] = value
        return self

    def setBody(self, newBody):
        self.body = newBody
        return self

    def addWaitCondition(self, condition, tries = -1):
        self.waits.append((condition, tries))
        return self

    def setMethod(self, method):
        self.method = method
        return self

    def do_request(self):
        verb_requester = getattr(requests, self.method)
        return verb_requester(url=url, json=body, headers=headers)

class WaitConditions:
    def ready(self, instance):
        return instance['state'] == InstanceState.READY
