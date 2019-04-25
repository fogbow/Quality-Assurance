# -*- coding: utf-8 -*-

import json
import sys
from authentication_service import AuthTest
from membership_service import MembersTest
from common import *
from os import path

def getresources(service_resources,required_resources):
    resources = {}
    jsonsuffix = '.json'

    for res in required_resources:
        resource_path = path.join(service_resources, res + jsonsuffix)
        resourcejson = Utils.load_json(resource_path)
        resources[res] = resourcejson

    return resources

if __name__ == "__main__":

    services = {
        'authentication_service': AuthTest,
        'membership_service': MembersTest
    }

    resources_path = 'test_resources'
    service_under_test = sys.argv[1]
    ServiceTest = services[service_under_test]

    test_config_path = path.join(resources_path, service_under_test, 'service_test_conf.json')
    configuration = Utils.load_json(test_config_path)

    service_resources_path = path.join(resources_path, service_under_test)
    service_resources = getresources(service_resources_path, ServiceTest.required_resources())

    print('###### Starting tests ######')

    servicetest = ServiceTest(service_under_test, configuration, service_resources)
    servicetest.setup()
    servicetest.run()
    servicetest.teardown()

    print('###### Tests are over ######')
