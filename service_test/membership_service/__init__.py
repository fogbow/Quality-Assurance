# -*- coding: utf-8 -*-

from .service_tests import *

modules = [service_tests]

__all__ = [prop for module in modules for prop in module.__all__]
