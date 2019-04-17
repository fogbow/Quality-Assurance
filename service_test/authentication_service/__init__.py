# -*- coding: utf-8 -*-

from .service_tests import *
from .general_configuration_test import *

modules = [service_tests, general_configuration_test]

__all__ = [prop for module in modules for prop in module.__all__]
