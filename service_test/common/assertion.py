# -*- coding: utf-8 -*-

""" Util class for TestSuite """
class Assertion(object):

    def __init__(self, suite, compare):
        self.compare = compare
        self.suite = suite

    def __call__(self, obtained, expected=None):
        print("Run to the hills", obtained, expected)

        assertresult = self.compare(obtained, expected) if expected \
            else self.compare(obtained)

        if assertresult:
            self.suite.assertion_ok()
        else:
            self.suite.assertion_fail()

    