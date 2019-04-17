# -*- coding: utf-8 -*-

import os
import re
import shutil
import subprocess
import sys
import tempfile
import uuid

from .constants import CommonConstants
from .utils import Utils

__all__ = ['TestSuite']

class TestSuite(object):

  test_number = 0
  workdir = tempfile.mkdtemp()

  def __init__(self, service):
    self.service = service
    self.service_dir = os.getcwd() + '/' + service
    self.service_instance = {}

  @classmethod
  def logTest(cls, msg):
    print("-- Test {}: {}".format(cls.which_test_case(), msg))

  @classmethod
  def whichtestcase(cls):
    cls.test_number += 1
    return cls.test_number

  def setup(self, pid):
    self.nope('setup')
    raise NotImplementedError

  def run(self):
    self.nope('run')
    raise NotImplementedError

  def teardown(self):
    self.nope('teardown')
    raise NotImplementedError

  def nope(self, phase):
    print('Not Implemented %s' % phase)

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

  # def set_branch(self, branch):
  #   os.system("git fetch")
  #   os.system("git checkout " + branch)

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
    print("I am at %s" % os.getcwd())
    self.copy_conf_files()

    outputfile = "log.out"

    command = "nohup %s > %s 2>&1 &" % (command, outputfile)
    print(command)

    subprocess.call(command, shell=True)
    return self.getpidbyport(port)

  def getpidbyport(self, port):
    temp_file_name = str(uuid.uuid4())
    with open(temp_file_name, 'w') as file:
      subprocess.call("lsof -t -i:%s" % port, shell=True, stdout=file)

    return Utils.file_get_contents(temp_file_name)

  def kill_background_process(self, pid):
    command = "kill -KILL %s " % pid
    os.system(command)
