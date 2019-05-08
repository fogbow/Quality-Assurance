# -*- coding: utf-8 -*-

from .service_test_instance import ServiceTestInstance
from .test_factory import TestEngine

__all__ = ['VersionCheck']

class VersionCheck(ServiceTestInstance):

    def run(self):
        self.version()

    def version(self):
        self.starttest('Requesting version')

        test = TestEngine(self.origin)
        res = test.get('version').json()
        version = res['version']
        
        self.assertgt(len(version), 0)
        
        self.endtest()