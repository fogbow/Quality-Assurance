# -*- coding: utf-8 -*-

""" Util class for ServiceTestInstance """
class Assertion(object):

    def __init__(self, suite, compare):
        self.compare = compare
        self.suite = suite

    def __call__(self, obtained, expected=None):
        if expected != None:
            assertpassed = self.compare(obtained,expected)
        else:
            assertpassed = self.compare(obtained)

        if assertpassed:
            self.suite.__assertion_ok__()
        else:
            self.suite.__assertion_fail__()

    