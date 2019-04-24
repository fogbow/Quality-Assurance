# -*- coding: utf-8 -*-

import requests
import shutil

from common import TestSuite, TestEngine

__all__ = ['AuthTest']

class AuthTest(TestSuite):

    def __init__(self, service, configuration, resources):
        TestSuite.__init__(self, service)
        self.conf = configuration
        self.pid = None
        self.resources = resources
        self.port = self.conf['application']['port']
        self.origin = 'http://localhost:' + str(self.port)

    def setup(self):
        repo_url = self.conf['application']['repo_url']
        branch = self.conf['application']['branch_under_test']

        self.clonerepo(repo_url, branch)

        command = self.conf['commands']['run_application']
        port = self.port

        pid = self.run_in_background(command, port)

        print("pid for proccess is %s" % pid)
        self.setpid(pid)

    def teardown(self):
        self.kill_background_process(self.pid)
        shutil.rmtree(self.workdir)

    def run(self):
        try:
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
        self.__createtokentest__('Fail attemp to creating token', \
            self.resources['invalid_auth_credentials'], \
            self.assertge)

    def __createtokentest__ (self, message, credentials, assertion):
        self.starttest(message)

        test = TestEngine(self.origin)
        res = test.create('token', body=credentials)
        
        assertion(res.status_code, 400)
        
        self.endtest()

    def setpid(self, pid):
        self.pid = pid

    @classmethod
    def required_resources(self):
        return ['auth_credentials', 'invalid_auth_credentials']
