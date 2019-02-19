#!/usr/bin/python

import sys
import os
import re

if len(sys.argv) == 1:
    print "No argument passed"
    exit(1)

if len(sys.argv) > 2:
    print "More than 1 parameter given"
    exit(-1)

with open(sys.argv[1]) as f:
    content = f.readlines()


for line in content:

    os.chdir('..')
    
    dependency, target = line.split('=')

    if target == '':
        target = 'develop'
    
    
    project = dependency.split("/")[-1].split(".")[0]
    repository = re.search("[^/]+(?=\.git)", dependency).group(0)
    
    os.system("git clone " + dependency)
    os.chdir(repository)
    os.system("git checkout " + target)
    os.system("mvn install")