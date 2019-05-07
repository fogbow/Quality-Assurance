# -*- coding: utf-8 -*-

import json
import os
import sys
from authentication_service import AuthTest
from membership_service import MembersTest
from resource_allocation_service import RASTest
from common import *

def getresources(service_resources,required_resources):
    resources = {}
    jsonsuffix = '.json'

    for res in required_resources:
        resource_path = os.path.join(service_resources, res + jsonsuffix)
        resourcejson = Utils.load_json(resource_path)
        resources[res] = resourcejson

    return resources

if __name__ == "__main__":

    curdir = os.getcwd()

    services = {
        'authentication_service': AuthTest,
        'membership_service': MembersTest,
        'resource_allocation_service': RASTest
    }

    resources_path = 'test_resources'
    service_under_test = sys.argv[1]
    ServiceTest = services[service_under_test]

    test_config_path = os.path.join(resources_path, service_under_test, 'service_test_conf.json')
    configuration = Utils.load_json(test_config_path)

    service_resources_path = os.path.join(resources_path, service_under_test)
    service_resources = getresources(service_resources_path, ServiceTest.required_resources())

    print('###### Starting tests ######')

    servicetest = ServiceTest(service_under_test, configuration, service_resources)
    servicetest.setup()
    servicetest.run()
    servicetest.teardown()

    print('###### Tests are over ######')
