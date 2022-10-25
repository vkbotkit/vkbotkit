"""
Copyright 2022 kensoi
"""

import asyncio
import logging
import os

import aiohttp

from .api import GetAPI

from .library import LibraryParser
from .longpoll import Longpoll
from .toolkit import ToolKit
from ..objects import exceptions
from ..objects.enums import LogLevel
from ..objects.data import Response
from ..utils import PATH_SEPARATOR, convert_to_package, toolkit_raise

logger = logging.getLogger("VKBotKit")


class Bot:
    """
    Объект бота
    """

    def __init__(self, access_token, group_id = None, api_version = "5.531",
            assets_path = None, library_path = None, trust_env: bool = False):

        self.access_token = access_token
        self.group_id = group_id
        self.api_version = api_version

        if not assets_path:
            assets_path = os.getcwd() + PATH_SEPARATOR + "assets"

        if not library_path:
            library_path = os.getcwd() + PATH_SEPARATOR + "library"

        self.session = aiohttp.ClientSession(trust_env=trust_env)
        self.longpoll = Longpoll(self.session, self._method)
        self.toolkit = ToolKit(self.api, assets_path)
        self.library = LibraryParser(library_path)
        self.__event_loop = asyncio.get_event_loop()


    def __repr__(self) -> str:
        return "<vkbotkit.framework.bot>"

    @property
    def api_url(self):
        """
        Прямой URL к API серверу ВКонтакте
        """

        return "https://api.vk.com/method/"

    @property
    def api(self):
        """
        Обёртка вокруг Bot._method()
        """

        return GetAPI(self.session, self._method)


    async def _method(self, method="groups.getById", params = None):
        """
        Скрытая функция для доступа к API
        """

        request_data = params or {}
        is_raw = request_data.pop("raw", False)

        if "access_token" not in request_data:
            request_data["access_token"] = self.access_token

        if "v" not in request_data:
            request_data["v"] = self.api_version

        response = await self.session.post(self.api_url + method, data = request_data)
        json = await response.json(content_type=None)

        if "response" in json:
            json = json['response']

        if isinstance(json, dict):
            if "error" in json:
                raise exceptions.MethodError(json["error"]["error_msg"])

            elif is_raw:
                return json

            else:
                return Response(json)

        elif isinstance(json, list):
            if is_raw:
                return json

            return [Response(i) for i in json]

        else:
            return json

    def close(self):
        """
        Метод для безопасного закрытия сессии бота
        """

        loop = asyncio.get_event_loop()
        map(lambda task: task.cancel(), asyncio.all_tasks(loop))
        loop.create_task(self.session.close())


    async def start_polling(self) -> None:
        """
        Начать обработку уведомлений с сервера ВКонтакте
        """

        if len(self.library.handlers) == 0:
            self.library.import_library(self.toolkit)

        if self.longpoll.is_polling:
            message = "polling already started"
            toolkit_raise(self.toolkit, message, LogLevel.ERROR, exceptions.LongpollError)

        self.toolkit.is_polling = True
        group_info = await self.toolkit.get_me()
        self.group_id = group_info.id

        await self.longpoll.update_server(self.group_id)
        self.toolkit.log(f"longpoll started at @{group_info.screen_name}")

        while self.toolkit.is_polling:
            for event in await self.longpoll.check(self.group_id):
                package = await convert_to_package(self.toolkit, event)
                parse_task = self.library.parse(self.toolkit, package)
                self.__event_loop.create_task(parse_task)

        self.close()
