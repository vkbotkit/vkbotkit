"""
Copyright 2023 kensoi
"""

import inspect


LIBRARY_REPR = '<vkbotkit.objects.callback.Library from module at path "{}">'

class Library:
    """
    Объект плагина
    """

    def __repr__(self):
        module = inspect.getmodule(self)
        module_path = module.__loader__.path

        return LIBRARY_REPR.format(module_path)
