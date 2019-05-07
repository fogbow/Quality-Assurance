# -*- coding: utf-8 -*-

from common import TestEngine, VersionandPublicKeyCheck

__all__ = ['AuthTest']

class AuthTest(VersionandPublicKeyCheck):

    def __init__(self, service, configuration, resources):
        super().__init__(service, configuration, resources)

    def run(self):
        try:
            super().run()
            self.createtoken()
            self.failcreatetoken()
        except Exception as e:
            self.fail()
            print("Interruped execution due to runtime error")
            raise e
        finally:
            self.logresults()

    def createtoken(self):
        self.__createtokentest__('Creating token', \
            self.resources['auth_credentials'], \
            self.assertlt)

    def failcreatetoken(self):
        self.__createtokentest__('Fail attemp to create token', \
            self.resources['invalid_auth_credentials'], \
            self.assertge)

    def __createtokentest__ (self, message, credentials, assertion):
        self.starttest(message)

        test = TestEngine(self.origin)
        res = test.create('token', body=credentials)
        
        assertion(res.status_code, 400)
        
        self.endtest()

    @classmethod
    def required_resources(self):
        return ['auth_credentials', 'invalid_auth_credentials']
