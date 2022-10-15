"""
Copyright 2022 kensoi
"""

import os

from .toolkit import ToolKit
from .library import CallbackLib
from ..utils import PATH_SEPARATOR

class Librabot:
    """
    Объект бота
    """

    def __init__(self, token, group_id = None, assetpath = None, libpath = None):
        if not assetpath:
            assetpath = os.getcwd() + PATH_SEPARATOR + "assets"

        if not libpath:
            libpath = os.getcwd() + PATH_SEPARATOR + "library"

        self.toolkit = ToolKit(token, group_id, assetpath)
        self.library = CallbackLib(libpath)


    def close(self):
        """
        Закрыть инструменты безопасно
        """

        self.toolkit.close()


    async def start_polling(self) -> None:
        """
        Начать обработку уведомлений с сервера ВКонтакте
        """

        await self.toolkit.start_polling(self.library)
