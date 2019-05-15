# -*- coding: utf-8 -*-

import copy
import time

from common import TestEngine, VersionandPublicKeyCheck
from . import RasModel

__all__ = ['RASTest']

class RASTest(VersionandPublicKeyCheck):

    def __init__(self, service, configuration, resources):
        super().__init__(service, configuration, resources)
        self.resources = resources

    def run(self):
        try:
            super().run()
            self.rasmodel = RasModel(self.origin, self.resources, self.conf)
            
            self.testgetimages()
            self.testgetimagebyid()

            self.testgetstatus()
            
            networkid = self.testcreatenetwork()
            computeid = self.testcreatecompute()
            volumeid = self.testcreatevolume()

            attachment = self.testcreateattachment(volumeid, computeid)
            computewithnetwork = self.testcreatecomputewithnetwork(networkid)
            
            self.testdeletenetworkwithcomputeattached(networkid)
            self.testdeleteattachedcompute(computeid)

        except Exception as e:

            self.fail()
            print("Interruped execution due to runtime error")
            print(e)
            raise e

        finally:
            self.logresults()

    def testgetstatus(self):
        resources = ['attachment', 'compute', 'network', 'publicIp', 'volume']

        for resource in resources:
            self.__testgetalloders__(resource)

    def testgetimages(self):
        self.starttest('GET Images')
        
        images = self.rasmodel.getimages()
        
        self.assertgt(len(images), 0)
        self.endtest()
    
    def testgetimagebyid(self):
        self.starttest('GET Image by id')
        
        imagedata = self.rasmodel.getimagebyid()

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

    def testcreatenetwork(self):
        return self.__testcreategenericorder__('network')

    def testcreatecompute(self):
        return self.__testcreategenericorder__('compute', True)

    def testcreatevolume(self):
        return self.__testcreategenericorder__('volume', True)

    def testcreateattachment(self, volumeid, computeid):
        self.starttest('POST attachment')
        
        body = self.__attachmentbodyrequests__(volumeid, computeid)
        res = self.rasmodel.create('attachment', body=body)
        
        self.assertlt(res.status_code, 400)
        
        self.endtest()
        ret = res.json()
        return ret['id']

    def testcreatecomputewithnetwork(self, network):
        self.starttest('POST compute passign some network')
        
        body = copy.deepcopy(self.resources['create_compute'])
        body['networkIds'] = [network]
        
        res = self.rasmodel.create('compute', body=body)
        
        self.assertlt(res.status_code, 400)
        self.endtest()

    def testdeletenetworkwithcomputeattached(self, network):
        self.starttest('DELETE network with orders attached (should fail)')
        
        res = self.rasmodel.delete('network', network)
        
        self.assertge(res.status_code, 400)
        self.endtest()

    @classmethod
    def required_resources(self):
        return ['auth_credentials', 'create_network', 'create_compute',
            'create_volume']

    def __testcreategenericorder__(self, resource, waitready=False):
        self.starttest('POST {}'.format(resource.capitalize()))

        res = self.rasmodel.creategenericorder(resource)
        
        self.assertlt(res.status_code, 400)
        
        _id = res.json()['id']

        if waitready:
            res = self.rasmodel.wait_until_ready(resource, _id)
            if not res:
                raise Exception('Wait for order to be ready failed, resource: {} , id: {}'.format(resource, _id))

        self.endtest()
        return res.json()['id']

    def __testgetalloders__(self, resource):
        self.starttest('GET {}s/status'.format(resource))
        
        response = self.rasmodel.getall(resource)
        self.assertlt(response.status_code, 400)

        self.endtest()

    def __attachmentbodyrequests__ (self, volumeid, computeid):
        return {
            "computeId": computeid,
            "volumeId": volumeid
        }
