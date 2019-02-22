# -*- coding: utf-8 -*-
__all__ = ['TestSuite']

class TestSuite:

    test_number = 0

    @classmethod
    def logTest(cls, msg):
        print("-- Test {}: {}".format(cls.which_test_case(), msg))

    @classmethod
    def which_test_case(cls):
        cls.test_number += 1
        return cls.test_number