# -*- coding: utf-8 -*-

from common import TestEngine

__all__ = ['RasModel']

class RasModel(object):

    def __init__(self, origin, resources, conf):
        self.resources = resources
        self.conf = conf
        self.__rasrequester__ = TestEngine(origin)
        
        pubkey = self.getpubkey()

        token = self.createtoken(pubkey)
        self.__rasrequester__.addHeader('Fogbow-User-Token', token)

        self.imageskwargs = {
            'memberid': self.conf['memberid'], 
            'cloud': self.conf['cloud']
        }

    def getpubkey(self):
        res = self.__rasrequester__.get('public-key').json()
        return res['publicKey']

    def createtoken(self, pubkey):
        
        as_url = self.conf['as_url']
        asrequester = TestEngine(as_url)

        credentials = self.resources['auth_credentials']
        credentials['publicKey'] = pubkey
        
        res = asrequester.create('token', body=credentials).json()
        return res['token']

    def create(self, resource, **kwargs):
        return self.__rasrequester__.create(resource, **kwargs)

    def get(self, resource, **kwargs):
        return self.__rasrequester__.get(resource, **kwargs)

    def getall(self, resource, **kwargs):
        return self.__rasrequester__.getall(resource, **kwargs)

    def getbyid(self, resource, _id, **kwargs):
        return self.__rasrequester__.getbyid(resource, _id, **kwargs)

    def delete(self, resource, _id, **kwargs):
        return self.__rasrequester__.delete(resource, _id, **kwargs)

    def creategenericorder(self, resource, parseresponse=False):
        body = self.resources['create_{}'.format(resource.lower())]
        res = self.__rasrequester__.create(resource.lower(), body=body)
        
        if parseresponse:
            res = res.json()['id']
        
        return res

    def wait_until_ready(self, resource, _id):
        return self.__rasrequester__.wait_until_ready(resource, _id)

    def getimages(self):
        res = self.__rasrequester__.get('images', **self.imageskwargs).json()
        return res.keys()
    
    def getimagebyid(self):
        res = self.__rasrequester__.get('images', **self.imageskwargs).json()
        images = list(res.keys())

        imageid = images[0]
        return self.__rasrequester__.getbyid('images', imageid, **self.imageskwargs).json()