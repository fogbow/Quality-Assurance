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

__all__ = ['TestSuite']

class TestSuite(object):

    test_number = 0
    workdir = tempfile.mkdtemp()

    def __init__(self, service):
        self.service = service
        self.service_dir = os.getcwd() + '/' + service
        self.service_instance = {}
        self.assert_count = 0
        self.assert_succ = 0
        self.failed_tests = []
        self.tests_info = {}

    @classmethod
    def starttest(cls, msg):
        testid = cls.nexttextcase()
        self.tests_info[testid] = msg
        print("-- Test {}: {}".format(testid, msg))

    @classmethod
    def endtest(cls, msg):
        if self.assert_count > 0:
            if self.assert_count != self.assert_succ:
                self.failed_tests.append(self.test_number)
            self.assert_count = 0
            self.assert_succ = 0

    @classmethod
    def nexttextcase(cls):
        cls.test_number += 1
        return cls.test_number

    def setup(self, pid):
        raise NotImplementedError

    def run(self):
        raise NotImplementedError

    def teardown(self):
        raise NotImplementedError

    @classmethod
    def required_resources(self):
        raise NotImplementedError

    def goto_workdir(self):
        if os.path.exists(self.workdir):
            shutil.rmtree(self.workdir)
        os.mkdir(self.workdir)
        os.chdir(self.workdir)

    def download_repo(self, url, branch):
        self.goto_workdir()

        os.system("git clone --single-branch --branch %s %s " % (branch, url))
        repository = re.search("[^/]+(?=\.git)", url).group(0)
        return repository

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
        shutil.rmtree(target)
        shutil.copytree(source, target)

    def run_in_background(self, command, port):
        print("service dir is %s" % self.service_dir)
        print("Workdir is %s" % os.getcwd())
        self.copy_conf_files()

        outputfile = "log.out"

        command = "nohup %s > %s 2>&1 &" % (command, outputfile)
        print(command)

        subprocess.call(command, shell=True)
        return self.getpidbyport(port)

    """ Use this with care """
    def getpidbyport(self, port):
        temp_file_name = str(uuid.uuid4())
        with open(temp_file_name, 'w') as file:
            subprocess.call("lsof -t -i:%s" % port, shell=True, stdout=file)

        content = Utils.file_get_contents(temp_file_name)
        if not content:
            time.sleep(1)
            return self.getpidbyport(port)
        return content

    def kill_background_process(self, pid):
        command = "kill -KILL %s " % pid
        os.system(command)

    def __getattribute__(self, attribute):
        func = object.__getattribute__(self, attribute)
        if not self.__issystemtestfunction__(attribute):
            return fun
        

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

    def __issystemtestfunction__(self, name):
        suite_functions = ['setup', 'run', 'teardown', 'required_resources']
        
        if name[0] == '_' or name in suite_functions:
            return False
        else:
            return True