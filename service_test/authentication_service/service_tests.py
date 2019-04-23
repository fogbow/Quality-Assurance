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
        self.createtoken()

    def createtoken(self):
        self.logTest('Creating token')
        test = TestEngine(self.origin)
        credentials = self.resources['auth_credentials']
        res = test.create('token', body=credentials)
        token = res['token']
        print('Token %s was obtained' % token)
        # body = json.lao

    def setpid(self, pid):
        self.pid = pid

    @classmethod
    def required_resources(self):
        return ['auth_credentials', 'invalid_auth_credentials']
