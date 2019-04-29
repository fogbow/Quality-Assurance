# -*- coding: utf-8 -*-

import requests
import shutil
import re

from common import TestEngine, VersionCheck

__all__ = ['MembersTest']

class MembersTest(VersionCheck):

    def __init__(self, service, configuration, resources):
        super().__init__(service, configuration, resources)

    def run(self):
        try:
            super().run()
            self.listmembers()
        except Exception as e:
            self.fail()
            print("Interruped execution due to runtime error")
            raise e
        finally:
            self.logresults()

    def listmembers(self):
        self.starttest('List members')
        
        test = TestEngine(self.origin)
        res = test.get('members').json()
        members = res['members']
        
        self.asserteq(type(members), list)
        self.assertge(len(members), 1)
        
        self.endtest()

    @classmethod
    def required_resources(self):
        return []
