# -*- coding: utf-8 -*-

import copy
import time

from common import FogbowHttpUtil, FogbowRequest, VersionandPublicKeyCheck, HttpMethods
from . import RasModel, RasUrls

__all__ = ['RASTest']

class RASTest(VersionandPublicKeyCheck):

    def __init__(self, service, configuration, resources):
        super().__init__(service, configuration, resources)
        self.resources = resources
    
    def run(self):
        self.rasmodel = RasModel(self.origin, self.resources, self.conf)
        res = self.rasmodel.get('cloud').json()
        clouds = res.get('clouds')

        # ms_url
        membersrequest = FogbowHttpUtil(self.conf['ms_url'])
        res = membersrequest.get('members').json()
        members = res.get('members')

        for member in members:
            for cloudio in clouds:
                print ('Running tests for member:', member, \
                    ', at cloud:', cloudio)
                
                self.tests_battery(member, cloudio)

    def tests_battery(self, memberid, cloudioname="emulated"):
        try:
            super().run()
            FogbowRequest.addsetting('body', {
                'provider': memberid,
                'cloudName': cloudioname
            })

            # GET {resource}/status
            images = self.testgetimages()
            self.testgetimagebyid(images)
            self.testgetstatus()

            # GET clouds
            self.testgetclouds()
            
            # Create a attachment
            computeid = self.testcreatecompute()
            volumeid = self.testcreatevolume()
            attachmentid = self.testcreateattachment(volumeid, computeid)
            
            self.test_fail_delete_compute_with_order_attached(computeid)
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

            # Create Public Ip
            computeid = self.testcreatecompute()
            publicip = self.testcreatepublicip(computeid)
            self.test_fail_delete_compute_with_order_attached(computeid)

            # Test Create SecurityRule over public ip
            securityrule = self.testcreatesecurityrule(publicip)
            self.testdeletepublicip(publicip)
            self.testdeletecompute(computeid)

        except Exception as e:

            self.fail()
            print("Interruped execution due to runtime error")
            print(e)
            raise e

        finally:
            self.logresults()

    def testgetstatus(self):
        resources = ['attachment', 'compute', 'network', 'public-ip', 'volume']

        for resource in resources:
            self.__testgetalloders__(resource)

    def testgetimages(self):
        self.starttest('GET Images')
        
        print('images received', )
        images = self.rasmodel.getimages()

        
        self.assertgt(len(images), 0)
        self.endtest()
        return images
    
    def testgetimagebyid(self, images):
        self.starttest('GET Image by id')
        _id = images[0]['id']
        
        imagedata = self.rasmodel.getimagebyid(_id)

        _name = imagedata['name']
        _size = imagedata['size']

        if self.asserteq(type(_id), str):
            self.assertgt(len(_id), 0)

        if self.asserteq(type(_name), str):
            self.assertgt(len(_name), 0)

        if self.asserteq(type(_size), int):
            self.assertgt(_size, 0)

        self.endtest()

    def testgetclouds(self):
        self.starttest("GET cloud(s)")
        cloudsendpoint = self.origin + '/clouds'
        cloudsresponse = self.rasmodel.genericrequest(cloudsendpoint)
        
        if self.assertlt(cloudsresponse.status_code, 400):
            
            clouds = cloudsresponse.json().get('clouds')
            
            self.asserteq(type(clouds), list)

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
        return ret.get('id')

    def testcreatecomputewithnetwork(self, networkid):
        self.starttest('POST compute passing a network')
        
        body = self.__getcompuebodyrequest__(networkid)
        
        res = self.rasmodel.create('compute', body=body)
        
        self.assertlt(res.status_code, 400)
        self.endtest()
        ret = res.json()
        return ret.get('id')

    def testcreatepublicip(self, computeid):
        self.starttest('POST public ip for compute: {}'.format(computeid))

        body = {'computeId': computeid}
        res = self.rasmodel.create('public-ip', body=body)
        _id = res.json().get('id')

        self.rasmodel.wait_until_ready('public-ip', _id)        
        
        self.assertlt(res.status_code, 400)
        self.endtest()
        
        return _id

    def test_fail_delete_network_with_compute_attached(self, networkid):
        self.__testfaildeletebusyorder__('network', networkid)

    def test_fail_delete_compute_with_order_attached(self, computeid):
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

    def testdeletepublicip(self, publicip):
        self.__testgenericdelete__('public-ip', publicip)

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

    def testcreatesecurityrule(self, pubip):
        self.starttest('POST security rule on public ip')
        
        body = self.resources['create_securityrule'].copy()
        res = self.rasmodel.create('secrule-publicip', body=body, pubip=pubip)
        _id = res.json().get('id')
        
        self.assertlt(res.status_code, 400)
        
        self.endtest()
        

    @classmethod
    def required_resources(self):
        return ['auth_credentials', 'create_network', 'create_compute',
            'create_volume', 'create_securityrule']

    def __testfaildeletebusyorder__(self, resource, _id):
        self.starttest('DELETE {} with orders attached (should fail)'.format(resource.capitalize()))
        
        res = self.rasmodel.delete(resource, _id)
        
        self.assertge(res.status_code, 400)
        self.endtest()

    def __testcreategenericorder__(self, resource, waitready=False):
        self.starttest('POST {}'.format(resource.capitalize()))

        res = self.rasmodel.creategenericorder(resource)
        
        self.assertlt(res.status_code, 400)
        
        _id = res.json().get('id')

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