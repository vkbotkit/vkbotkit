"""
Copyright 2022 kensoi
"""

from . import data, enums, exceptions, filters, keyboard
from ..framework.decorators import callback, Handler
from ..framework.utils import Mention

NAME_CASES = ['nom', 'gen','dat', 'acc', 'ins', 'abl']

class LibraryModule:
    """
    Объект плагина
    """

    def __init__(self):
        methods = set(dir(self)) - set(dir(object()))

        objs = map(lambda i: getattr(self, i), methods)
        funcs = filter(callable, objs)
        decs = map(lambda i: i(), funcs)
        callbacks = filter(lambda i: isinstance(i, Handler), decs)
        self.handlers = list(callbacks)
