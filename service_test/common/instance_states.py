# -*- coding: utf-8 -*-
from enum import Enum, auto

__all__ = ['InstanceState']

class InstanceState(Enum):
    DISPATCHED = auto()
    READY = auto()
    CREATING = auto()
    UNAVAILABLE = auto()
    FAILED = auto()
    INCONSISTENT = auto()
