# -*- coding: utf-8 -*-

""" Util class for TestSuite """
class Assertion(object):

    def __init__(self, suite, compare):
        self.compare = compare
        self.suite = suite

    def __call__(self, obtained, expected=None):
        assertpassed = self.compare(obtained, expected) if expected \
            else self.compare(obtained)

        if assertpassed:
            self.suite.__assertion_ok__()
        else:
            self.suite.__assertion_fail__()

    