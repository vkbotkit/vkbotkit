"""
Copyright 2022 kensoi
"""

import os
from ..utils import PATH_SEPARATOR

class Assets:
    """
    Рабочий класс для работы с медиафайлами из каталога ассетов.
    """

    def __init__(self, sdk, assets = None):
        if not assets:
            assets = PATH_SEPARATOR.join([os.getcwd(), "assets", ""])

        if assets[-1] != PATH_SEPARATOR:
            assets += PATH_SEPARATOR

        if assets.startswith("."):
            assets = os.getcwd() + assets[1:]

        if not os.path.exists(assets):
            os.mkdir(assets)
            sdk.log(message = "Assets directory was made by framework")

        if not os.path.isdir(assets):
            raise Exception("Assets directory should be a folder")

        self.__path = assets


    def __call__(self, *args, **kwargs):
        args = list(args)

        if len(args) > 0:
            args[0] = self.__path + args[0]

        elif 'file' in kwargs:
            kwargs['file'] = self.__path + kwargs['file']

        encoding = kwargs.pop('encoding') if 'encoding' in kwargs else "utf-8"

        return open(encoding = encoding, *args, **kwargs)


    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def __repr__(self) -> str:
        return "<vkbotkit.features.Assets>"
