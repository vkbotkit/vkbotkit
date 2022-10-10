"""
Copyright 2022 kensoi
"""

from ..framework.decorators import Handler
from ..framework.utils import Mention

NAME_CASES = ['nom', 'gen','dat', 'acc', 'ins', 'abl']

def callback(callback_filter):
    """
    Прикрепить к обработчику фильтры
    """

    return lambda function: lambda self: Handler(callback_filter, function, self)

class LibraryModule:
    """
    Объект плагина
    """

    def __init__(self):
        methods = set(dir(self)) - set(dir(object()))

        methods_map = map(lambda i: getattr(self, i), methods)
        methods_filtered = filter(callable, methods_map)
        methods_inited = map(lambda i: i(), methods_filtered)
        self.handlers = list(filter(lambda i: isinstance(i, Handler), methods_inited))
