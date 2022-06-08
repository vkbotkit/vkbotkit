"""
Copyright 2022 kensoi
"""

import os
from . import (
    data, decorators, enums, exceptions, keyboard
)

PATH_SEPARATOR = "\\" if os.name == 'nt' else "/"

class LibraryModule:
    """
    Объект плагина
    """
    def __init__(self):
        """
        docstring patch
        """

        attrs_a = dir(self)
        attrs_b = dir(object())

        set_a = set(attrs_a)
        set_b = set(attrs_b)
        self._handlers = []
        methods = set_a - set_b
        for i in methods:
            method = getattr(self, i)
            if callable(method):
                obj = method()
                if isinstance(obj, decorators.Handler):
                    self._handlers.append(obj)
