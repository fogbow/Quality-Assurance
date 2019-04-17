# -*- coding: utf-8 -*-

import json

__all__ = ['Utils']

class Utils:

    @classmethod
    def file_get_contents(self, filename):
        with open(filename) as f:
            return f.read()

    @classmethod
    def load_json(self, filename):
        json_data = self.file_get_contents(filename)
        return json.loads(json_data)
