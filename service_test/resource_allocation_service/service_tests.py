# -*- coding: utf-8 -*-

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
            self.getimages()
            self.getimagebyid()
        except Exception as e:
            self.fail()
            print("Interruped execution due to runtime error")
            raise e
        finally:
            self.logresults()

    def getimages(self):
        self.starttest('GET Images')
        
        res = self.__rasrequester__.get('images', **self.imageskwargs).json()
        images = res.keys()
        
        self.assertgt(len(images), 0)
        self.endtest()

    def getimagebyid(self):
        self.starttest('GET Image by id')
        
        res = self.__rasrequester__.get('images', **self.imageskwargs).json()
        images = list(res.keys())

        imageid = images[0]
        imagedata = self.__rasrequester__.getbyid('images', imageid, **self.imageskwargs).json()

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

    def createnetwork(self):
        pass

    def createcompute(self):
        pass

    def createvolume(self):
        pass

    def createattachment(self):
        pass

    @classmethod
    def required_resources(self):
        return ['auth_credentials']

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