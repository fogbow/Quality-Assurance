#!/usr/bin/python

import sys
import os
import re

if len(sys.argv) == 1:
    print("No argument passed")
    exit(1)

if len(sys.argv) > 2:
    print("More than 1 parameter given")
    exit(-1)

with open(sys.argv[1]) as f:
    content = f.readlines()

for line in content:

    os.chdir('..')

    dependency, target = line.split('=')

    if target == None or target == '':
        target = 'develop'

    project = dependency.split("/")[-1].split(".")[0]
    repository = re.search("[^/]+(?=\.git)", dependency).group(0)

    print("> git clone \"%s\" into \"%s\"" % (dependency, project))
    os.system("git clone " + dependency)

    print("> cd %s" % repository)
    os.chdir(repository)

    print("> git checkout " + target)
    os.system("git checkout " + target)

    print(os.getcwd())

    print("> mvn install")
    os.system("mvn install")