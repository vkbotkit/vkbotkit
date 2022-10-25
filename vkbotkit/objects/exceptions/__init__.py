"""
Copyright 2022 kensoi
"""

from .library import *
from .longpoll import *


class InvalidMention(ValueError):
    """
    Ошибка, связанная с некорректным Mention
    """

class InvalidPackage(TypeError):
    """
    Объект не унаследован и/или не пренадлежит vkbotkit.objects.data.Package
    """

class MethodError(Exception):
    """
    Исключение, вызванное ошибкой в результате запроса на сервер ВКонтакте.
    Проверьте параметры запроса
    """
