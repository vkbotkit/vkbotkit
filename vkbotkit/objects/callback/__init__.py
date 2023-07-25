"""
Copyright 2022 kensoi
"""

from .wrapper import Wrapper

def callback(command_filter):
    """
    Прикрепить к обработчику фильтры
    """

    def decorator(command_handler):
        def wrapper(self):
            return Wrapper(command_filter, command_handler, self)

        return wrapper

    return decorator
