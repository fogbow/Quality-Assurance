# -*- coding: utf-8 -*-

import operator
import os
import re
import shutil
import subprocess
import tempfile
import time
import uuid

from .constants import CommonConstants
from .utils import Utils
from .assertion import Assertion

__all__ = ['ServiceTestInstance']

class ServiceTestInstance(object):

    test_number = 0
    workdir = tempfile.mkdtemp()
    failed_tests = []
    tests_info = {}
    assert_count = 0
    assert_succ = 0

    def __init__(self, service, configuration, resources):
        self.conf = configuration
        self.service = service
        self.service_dir = os.getcwd() + '/' + service
        self.pid = None
        self.resources = resources
        self.port = self.conf['application']['port']
        self.origin = 'http://localhost:' + str(self.port)

    def starttest(cls, msg):
        cls.endtest()
        testid = cls.nexttextcase()
        cls.tests_info[testid] = msg
        print("\n-- Test {}: {}".format(testid, msg))

    def endtest(cls):
        if cls.assert_count > 0:
            if cls.assert_count != cls.assert_succ:
                cls.failed_tests.append(cls.test_number)
        cls.assert_count = 0
        cls.assert_succ = 0

    def fail(cls):
        cls.assert_count += 1

    def logresults(cls):
        print("%d tests were run" % cls.test_number)
        print("%d tests passed" % (cls.test_number - len(cls.failed_tests)))
        print("%d tests failed" % len(cls.failed_tests))
        
        if cls.failed_tests:
            print("\n\n-- Failed tests --\n\n")
            for test in cls.failed_tests:
                print("%d -- %s" % (test, cls.tests_info[test]))

    @classmethod
    def nexttextcase(cls):
        cls.test_number += 1
        return cls.test_number

    def run(self):
        raise NotImplementedError

    @classmethod
    def required_resources(self):
        raise NotImplementedError
    
    def setup(self):
        repo_url = self.conf['application']['repo_url']
        branch = self.conf['application']['branch_under_test']

        self.clonerepo(repo_url, branch)

        command = self.conf['commands']['run_application']
        port = self.port

        pid = self.run_in_background(command, port)
        if not pid:
            print('Could not start the service. Exiting...')
            exit(-1)

        print("pid for proccess is %s" % pid)
        self.pid = pid

    def teardown(self):
        self.kill_background_process(self.pid)
        shutil.rmtree(self.workdir)

    def goto_workdir(self):
        if os.path.exists(self.workdir):
            shutil.rmtree(self.workdir)
        os.mkdir(self.workdir)
        os.chdir(self.workdir)

    def download_repo(self, url, branch):
        self.goto_workdir()

        self.__runcommand__("git clone --single-branch --branch %s %s " % (branch, url))
        repository = re.search("[^/]+(?=\.git)", url).group(0)
        return repository

    def install_dependencies(self):
        dep_propr_path = self.workdir + '/' + CommonConstants.resource_path + \
            CommonConstants.dependencies_properties
        
        script = CommonConstants.install_dependencies_script.format(self.service_dir)
        
        command = '{} {}'.format(script, dep_propr_path)
        self.__runcommand__(command)
        os.chdir(self.workdir)

    def clonerepo(self, url, branch = "master"):
        repository = self.download_repo(url, branch)

        self.workdir = os.getcwd() + '/' + repository
        os.chdir(self.workdir)

        self.reponame = repository
        
        return self.workdir

    def copy_conf_files(self):
        source = '/'.join([self.service_dir, CommonConstants.private])
        target = '/'.join([os.getcwd(), CommonConstants.resource_path, \
            CommonConstants.private])

        print('Configuration files source is "%s" and target is "%s"' % (source, target))

        # It's important to remove any noise from destination folder
        if os.path.exists(target):
            shutil.rmtree(target)
        
        shutil.copytree(source, target)

    def run_in_background(self, command, port):
        self.install_dependencies()
        print("Service dir is %s" % self.service_dir)
        print("Workdir is %s" % os.getcwd())
        self.copy_conf_files()

        outputfile = "log.out"

        command = "nohup %s > %s 2>&1 &" % (command, outputfile)
        print(command)

        subprocess.call(command, shell=True)
        return self.getpidbyport(port)

    """ Use this with care """
    def getpidbyport(self, port, ttl=50):
        if ttl <= 0:
            return ''

        temp_file_name = str(uuid.uuid4())
        with open(temp_file_name, 'w') as file:
            subprocess.call("lsof -t -i:%s" % port, shell=True, stdout=file)

        content = Utils.file_get_contents(temp_file_name)
        if not content:
            time.sleep(1)
            return self.getpidbyport(port, ttl-1)
        return content

    def kill_background_process(self, pid):
        command = "kill -KILL %s " % pid
        self.__runcommand__(command)

    def __getattr__(self, attribute):
        comparation_functions = ['eq', 'ne', 'lt', 'le', 'gt', 'ge']
        assertstr = 'assert'
        for cmp in comparation_functions:
            if(attribute == assertstr+cmp):
                return Assertion(self, getattr(operator, cmp))
            
        raise AttributeError

    def __assertion_ok__(self):
        self.assert_count += 1
        self.assert_succ += 1

    def __assertion_fail__(self):
        self.assert_count += 1

    def __runcommand__(self, command):
        print('\n>', command)
        os.system(command)