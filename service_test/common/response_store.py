# -*- coding: utf-8 -*-

from collections import defaultdict

__all__ = ['ResourceStore']

class ResourceStore:
    data = defaultdict(list)

    @classmethod
    def addresourceid(cls, resource, resid):
        cls.data[resource].append(resid)

    @classmethod
    def getresourceidd(cls, resource):
        return cls.data[resource]