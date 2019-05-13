# -*- coding: utf-8 -*-

import time
from common import TestEngine, VersionandPublicKeyCheck

__all__ = ['RASTest']

class RASTest(VersionandPublicKeyCheck):

    def __init__(self, service, configuration, resources):
        super().__init__(service, configuration, resources)
        
        self.imageskwargs = {
            'memberid': self.conf['memberid'], 
            'cloud': self.conf['cloud']
        }

    def run(self):
        self.__rasrequester__ = TestEngine(self.origin)
        
        pubkey = self.__getpubkey__()

        token = self.__createtoken__(pubkey)
        self.__rasrequester__.addHeader('Fogbow-User-Token', token)
        
        try:
            super().run()
            
            self.testgetimages()
            self.testgetimagebyid()
            
            networkid = self.createnetwork()
            computeid = self.createcompute()
            volumeid = self.createvolume()

            # # remove after implementing wait
            # time.sleep(10)

            attachment = self.createattachment(volumeid, computeid)
        except Exception as e:
            self.fail()
            print("Interruped execution due to runtime error")
            raise e
        finally:
            self.logresults()

    def testgetimages(self):
        self.starttest('GET Images')
        
        images = self.getimages()
        
        self.assertgt(len(images), 0)
        self.endtest()
    
    def testgetimagebyid(self):
        self.starttest('GET Image by id')
        
        imagedata = self.getimagebyid()

        _id = imagedata['id']
        _name = imagedata['name']
        _size = imagedata['size']

        if self.asserteq(type(_id), str):
            self.assertgt(len(_id), 0)

        if self.asserteq(type(_name), str):
            self.assertgt(len(_name), 0)

        if self.asserteq(type(_size), int):
            self.assertgt(_size, 0)

        self.endtest()

    def getimages(self):
        res = self.__rasrequester__.get('images', **self.imageskwargs).json()
        return res.keys()

    def getimagebyid(self):
        res = self.__rasrequester__.get('images', **self.imageskwargs).json()
        images = list(res.keys())

        imageid = images[0]
        return self.__rasrequester__.getbyid('images', imageid, **self.imageskwargs).json()

    def createnetwork(self):
        return self.__testgenericorder__('network')

    def createcompute(self):
        return self.__testgenericorder__('compute', True)

    def createvolume(self):
        return self.__testgenericorder__('volume', True)

    def createattachment(self, volumeid, computeid):
        self.starttest('POST attachment')
        
        body = self.__attachmentbodyrequests__(volumeid, computeid)
        res = self.__rasrequester__.create('attachment', body=body)
        
        self.assertlt(res.status_code, 400)
        
        self.endtest()
        ret = res.json()
        return ret['id']

    @classmethod
    def required_resources(self):
        return ['auth_credentials', 'create_network', 'create_compute',
            'create_volume']

    def __getpubkey__(self):
        res = self.__rasrequester__.get('public-key').json()
        return res['publicKey']

    def __createtoken__(self, pubkey):
        
        as_url = self.conf['as_url']
        asrequester = TestEngine(as_url)

        credentials = self.resources['auth_credentials']
        credentials['publicKey'] = pubkey
        
        res = asrequester.create('token', body=credentials).json()
        return res['token']

    def __creategenericorder__(self, resource, parseresponse=False):
        body = self.resources['create_{}'.format(resource.lower())]
        res = self.__rasrequester__.create(resource.lower(), body=body)
        
        if parseresponse:
            res = res.json()['id']
        
        return res

    def __testgenericorder__(self, resource, waitready=False):
        self.starttest('POST {}'.format(resource.capitalize()))

        res = self.__creategenericorder__(resource)
        
        self.assertlt(res.status_code, 400)
        
        _id = res.json()['id']

        if waitready:
            res = self.__rasrequester__.wait_until_ready(resource, _id)
            if not res:
                raise Exception('Wait for order to be ready failed, resource: {} , id: {}'.format(resource, _id))

        self.endtest()
        return res.json()['id']

    def __attachmentbodyrequests__ (self, volumeid, computeid):
        return {
            "computeId": volumeid,
            "volumeId": computeid
        }