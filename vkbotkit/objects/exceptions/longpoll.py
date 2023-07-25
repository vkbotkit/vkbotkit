"""
Copyright 2023 kensoi
"""

from .library import LibraryException


class LongpollError(LibraryException):
    """
    Ошибка, связанная с Longpoll
    """

class UnsupportedEvent(LongpollError):
    """
    Ошибка, вызванная неподдерживаемым событием VK Longpoll
    """
