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

    def getimages(self):
        pass

    def createnetwork(self):
        pass

    def createcompute(self):
        pass

    def createvolume(self):
        pass

    def createattachment(self):
        pass

    @classmethod
    def required_resources(self):
        return []
