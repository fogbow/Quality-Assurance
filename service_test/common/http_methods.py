# -*- coding: utf-8 -*-

from enum import Enum, auto

__all__ = ['HttpMethods']

class HttpMethods(Enum):
    DELETE = 'delete'
    GET = 'get'
    POST = 'post'
