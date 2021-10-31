from . import (
    data, decorators, enums, exceptions, keyboard
)

class libraryModule:
    def __init__(self):
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
                if isinstance(obj, decorators.handler):
                    self._handlers.append(obj)