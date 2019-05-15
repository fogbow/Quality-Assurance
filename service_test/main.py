# -*- coding: utf-8 -*-

import os
import sys
from authentication_service import AuthTest
from membership_service import MembersTest
from resource_allocation_service import RASTest
from common import *

SKIP_SETUP_FLAG = '--skip-setup'
SKIP_TEARDOWN_FLAG = '--skip-teardown'
resources_path = 'test_resources'

def getresources(service_resources ,required_resources):
    resources = {}
    jsonsuffix = '.json'

    for res in required_resources:
        resource_path = os.path.join(service_resources, res + jsonsuffix)
        resourcejson = Utils.load_json(resource_path)
        resources[res] = resourcejson

    return resources

def getserviceconf(servicename):
    test_config_path = os.path.join(resources_path, servicename, 'service_test_conf.json')
    return Utils.load_json(test_config_path)

def getservice(servicename):
    services = {
        'authentication_service': AuthTest,
        'membership_service': MembersTest,
        'resource_allocation_service': RASTest
    }
    
    ServiceTest = services[servicename]

    configuration = getserviceconf(servicename)

    service_resources_path = os.path.join(resources_path, servicename)
    service_resources = getresources(service_resources_path, ServiceTest.required_resources())

    return ServiceTest(servicename, configuration, service_resources)

if __name__ == "__main__":

    curdir = os.getcwd()

    service_under_test = sys.argv[1]

    servicetest = getservice(service_under_test)
    conf = getserviceconf(service_under_test)
    dependencies_services = []

    print('###### Starting tests ######')
    
    runsetup = SKIP_SETUP_FLAG not in sys.argv

    if runsetup:

        # start dependencies services
        for servicename in conf['services']:
            serviceinstance = getservice(servicename)
            serviceinstance.setup()
            serviceinstance.run()
            
            dependencies_services.append(serviceinstance)
            
            # those setups may change current dir
            os.chdir(curdir)


        servicetest.setup()
        
    servicetest.run()

    print('###### Tests are over ######')

    runteardown = SKIP_TEARDOWN_FLAG not in sys.argv

    if runteardown:
        print('######  Tearing down  ######')

        servicetest.teardown()
        
        for serviceinstance in dependencies_services:
            serviceinstance.teardown()
            
            # these teardowns may change current dir
            os.chdir(curdir)

    print('######  Done  ######')
