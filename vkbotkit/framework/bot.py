"""
Copyright 2022 kensoi
"""

import asyncio
import logging
import os
import typing

import aiohttp

from vkbotkit.framework.features.api import GetAPI

from .features import LibraryParser, Longpoll, ToolKit
from ..objects import exceptions, data, enums
from ..utils import PATH_SEPARATOR

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


    @property
    def api_url(self):
        """
        docstring patch
        """

        return "https://api.vk.com/method/"

    @property
    def api(self):
        """
        docstring patch
        """

        return GetAPI(self.session, self._method)


    async def _method(self, method="groups.getById", params = None):
        """
        docstring patch
        """

        request_data = params or {}
        is_raw = request_data.pop("raw", False)

        if "access_token" not in request_data:
            request_data["access_token"] = self.access_token

        if "v" not in request_data:
            request_data["v"] = self.api_version

        logger.log(10, "method '%s' was called with params %s", method, str(request_data))

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
                return data.Response(json)

        elif isinstance(json, list):
            if is_raw:
                return json

            return [data.Response(i) for i in json]

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
            self.library.import_library(self)

        if self.longpoll.is_polling:
            self.toolkit.log("polling already started", log_level=enums.LogLevel.ERROR)
            raise Exception("polling already started")

        self.toolkit.is_polling = True
        group_info = await self.toolkit.get_me()
        await self.longpoll.update_server(group_info.id)
        self.toolkit.log(f"longpoll started at @{group_info.screen_name}")

        while self.toolkit.is_polling:
            for event in await self.longpoll.check(group_info.id):
                self.__event_loop.create_task(self.library.parse(self, event))

        self.close()
