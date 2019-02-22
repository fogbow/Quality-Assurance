# -*- coding: utf-8 -*-
from .test_suite import *

commons = [test_suite]

__all__ = [prop for common in commons for prop in common.__all__]