# -*- coding: utf-8 -*-

from .service_test_instance import ServiceTestInstance
from .test_factory import TestEngine
from .check_version import VersionCheck

__all__ = ['VersionandPublicKeyCheck']

class VersionandPublicKeyCheck(VersionCheck):

    def run(self):
        super().run()
        self.publickey()

    def publickey(self):
        self.starttest('Requesting public key')

        test = TestEngine(self.origin)
        res = test.get('public-key').json()
        publickey = res['publicKey']
        
        self.assertgt(len(publickey), 0)

        self.endtest()