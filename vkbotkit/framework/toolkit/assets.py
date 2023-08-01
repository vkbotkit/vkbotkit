"""
Copyright 2023 kensoi
"""

import os

from ...objects.enums import LogLevel
from ...utils import toolkit_raise


class Assets:
    """
    Рабочий класс для работы с медиафайлами из каталога ассетов.
    """

    def __init__(self, toolkit):
        self.path = os.path.join(os.getcwd(), "assets")

        if not os.path.exists(self.path):
            os.mkdir(self.path)
            toolkit.log(message = "Assets directory was made by framework",
                        log_level = LogLevel.DEBUG)

        if not os.path.isdir(self.path):
            toolkit_raise(toolkit, "Assets directory should be a folder", LogLevel.DEBUG, Exception)


    def __call__(self, *args, **kwargs):
        args = list(args)

        if len(args) > 0:
            args[0] = self.path + args[0]

        elif 'file' in kwargs:
            kwargs['file'] = os.path.join(self.path, kwargs['file'])

        encoding = kwargs.pop('encoding', "utf-8")

        return open(encoding = encoding, *args, **kwargs)


    def __repr__(self) -> str:
        return "<vkbotkit.framework.toolkit.assets>"
