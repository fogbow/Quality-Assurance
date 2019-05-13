# -*- coding: utf-8 -*-

import json
import requests

from os import path
from . import HttpMethods

__all__ = ['TestEngine']

class TestEngine(object):
    def __init__(self, service_url):
        self.last_create = None
        self.service_url = service_url;
        self.body = {}
        self.headers = {}

    def wait_until_ready(self, resource, instance_id, tries = 50):
        if tries <= 0:
            return None
        
        res = self.getbyid(resource, id)

        if res['state'] == InstanceState.READY:
            ret = res
        else:
            ret = self.wait_until_ready(tries-1)

        return ret

    def create(self, resource, **kwargs):
        url = self.__getserviceendpoint__(resource, **kwargs)

        headers = kwargs.get('headers', self.headers)
        body    = kwargs.get('body', self.body)

        req = FogbowRequest(url=url, headers=headers, body=body, method=str(HttpMethods.POST))
        self.last_create = req.execute()

        return self.last_create

    def get(self, resource, **kwargs):
        url = self.__getserviceendpoint__(resource, **kwargs)

        return self.__executeget__(url, **kwargs)

    def getbyid(self, resource, _id, **kwargs):
        url = self.__getserviceendpoint__(resource, **kwargs)

        url = url + '/' + _id

        return self.__executeget__(url, **kwargs)

    def __executeget__(self, url, **kwargs):
        
        headers = kwargs.get('headers', self.headers)
        body    = kwargs.get('body', self.body)

        req = FogbowRequest(url=url, headers=headers, body=body, method=str(HttpMethods.GET))
        
        return req.execute()

    def __getserviceendpoint__(self, resource, **kwargs):
        memberid = kwargs.get('memberid', '')
        cloud = kwargs.get('cloud', '')

        available_endpoints = {
            'token': '/tokens',
            'images': '/images/{}/{}/'.format(memberid, cloud),
            'members': '/members',
            'version': '/version',
            'public-key': '/publicKey',
            'networks': '/networks',
            'compute': '/computes',
            'volume': '/volumes',
            'attachment': '/attachments'
        }

        urlpath = available_endpoints[resource]
        url = self.service_url + '/' + urlpath

        return url

    def addHeader(self, header, headervalue):
        if header and headervalue:
            print('Setting default header "{}" to "{}"'.format(header, headervalue))
            self.headers[header] = headervalue
        else:
            print("Ignoring header setting. One or more parameters were empty.")
            print("Header: {}".format(header))
            print("Header content: {}".format(headervalue))

class FogbowRequest:
    def __init__(self, url, method = 'get', body = {}, headers = {}):
        self.url = url
        self.headers = headers
        self.body = body
        self.method = method

    def execute(self):
        verb_requester = getattr(requests, self.method)
        res = verb_requester(url=self.url, json=self.body, headers=self.headers)

        print("\n---- Begin Response ----\n")
        print("url: %s\n" % res.url)
        print("headers: %s\n" % res.headers)
        print("json: %s\n" % res.json())
        print("\n----  End Response  ----\n")

        return res
