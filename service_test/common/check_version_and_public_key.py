# -*- coding: utf-8 -*-

from .service_test_instance import ServiceTestInstance
from .test_factory import TestEngine
from .check_version import VersionCheck

__all__ = ['VersionandPublicKeyCheck']

class VersionandPublicKeyCheck(VersionCheck):

    def __init__(self, service, configuration, resources):
        return super().__init__(service, configuration, resources)

    def run(self):
        super().run()
        self.publickey()

    def publickey(self):
        self.starttest('Requesting public key')

        test = TestEngine(self.origin)
        res = test.get('public-key').json()
        publickey = res['publicKey']
        
        self.asserteq(len(publickey)%3, 0)
        
        self.endtest()