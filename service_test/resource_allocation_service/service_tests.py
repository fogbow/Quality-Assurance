# -*- coding: utf-8 -*-

from common import TestEngine, VersionandPublicKeyCheck

__all__ = ['RASTest']

class RASTest(VersionandPublicKeyCheck):

    def __init__(self, service, configuration, resources):
        super().__init__(service, configuration, resources)

    def run(self):
        try:
            super().run()
        except Exception as e:
            self.fail()
            print("Interruped execution due to runtime error")
            raise e
        finally:
            self.logresults()

    @classmethod
    def required_resources(self):
        return []
