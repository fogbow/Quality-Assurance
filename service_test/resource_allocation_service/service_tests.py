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

            # # GET {resource}/status
            self.testgetimages()
            self.testgetimagebyid()
            self.testgetstatus()

            
            # Create a attachment
            computeid = self.testcreatecompute()
            volumeid = self.testcreatevolume()
            attachmentid = self.testcreateattachment(volumeid, computeid)
            
            self.test_fail_delete_compute_with_volume_attached(computeid)
            self.test_fail_delete_volume_attached_to_compute(volumeid)

            self.testdeleteattchment(attachmentid)
            self.testdeletecompute(computeid)
            self.testdeletevolume(volumeid)
            
            # Create a single computes in the same network
            networkid = self.testcreatenetwork()
            computewithnetwork = self.testcreatecomputewithnetwork(networkid)
            self.test_fail_delete_network_with_compute_attached(networkid)
            self.testdeletecompute(computewithnetwork)
            self.testdeletenetwork(networkid)

            # Create a bunch of computes in the same network
            networkid = self.testcreatenetwork()
            computes = self.testcreatemanycomputeswithnetwork(networkid)
            self.test_fail_delete_network_with_compute_attached(networkid)
            self.testdeletemanycomputes(computes)
            self.testdeletenetwork(networkid)

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
        return self.__testcreategenericorder__('network', True)

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

    def testcreatecomputewithnetwork(self, networkid):
        self.starttest('POST compute passing a network')
        
        body = self.__getcompuebodyrequest__(networkid)
        
        res = self.rasmodel.create('compute', body=body)
        
        self.assertlt(res.status_code, 400)
        self.endtest()
        ret = res.json()
        return ret['id']

    def test_fail_delete_network_with_compute_attached(self, networkid):
        self.__testfaildeletebusyorder__('network', networkid)

    def test_fail_delete_compute_with_volume_attached(self, computeid):
        self.__testfaildeletebusyorder__('compute', computeid)

    def test_fail_delete_volume_attached_to_compute(self, volumeid):
        self.__testfaildeletebusyorder__('volume', volumeid)

    def testdeleteattchment(self, attachmentid):
        self.__testgenericdelete__('attachment', attachmentid)
    
    def testdeletecompute(self, computeid):
        self.__testgenericdelete__('compute', computeid)
    
    def testdeletevolume(self, volumeid):
        self.__testgenericdelete__('volume', volumeid)

    def testdeletenetwork(self, networkid):
        self.__testgenericdelete__('network', networkid)

    def testcreatemanycomputeswithnetwork(self, networkid, howmany=5):
        self.starttest("POST many computes with network {}".format(networkid))

        body = self.__getcompuebodyrequest__(networkid)
        computesresponses = self.rasmodel.createmany('compute', howmany, body=body, wait_ready=True)

        for res in computesresponses:
            self.assertlt(res.status_code, 400)

        self.endtest()
        return computesresponses

    def testdeletemanycomputes(self, computes):
        self.starttest("Deleting many computes")

        for compute in computes:
            data = compute.json()
            computeid = data['id']
            response = self.rasmodel.delete('compute', computeid)
            self.assertlt(response.status_code, 400)

        self.endtest()

    @classmethod
    def required_resources(self):
        return ['auth_credentials', 'create_network', 'create_compute',
            'create_volume']

    def __testfaildeletebusyorder__(self, resource, _id):
        self.starttest('DELETE {} with orders attached (should fail)'.format(resource.capitalize()))
        
        res = self.rasmodel.delete(resource, _id)
        
        self.assertge(res.status_code, 400)
        self.endtest()

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

    def __testgenericdelete__(self, resource, _id):
        self.starttest('DELETE {} with id {}'.format(resource.capitalize(), _id))

        res = self.rasmodel.delete(resource, _id)
        
        self.assertlt(res.status_code, 400)
        self.endtest()

    def __attachmentbodyrequests__ (self, volumeid, computeid):
        return {
            "computeId": computeid,
            "volumeId": volumeid
        }

    def __getcompuebodyrequest__(self, networkid):
        body = copy.deepcopy(self.resources['create_compute'])
        body['networkIds'] = [networkid]
        return body