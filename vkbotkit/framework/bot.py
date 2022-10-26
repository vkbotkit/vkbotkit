"""
Copyright 2022 kensoi
"""

import asyncio
import os
import typing
import aiohttp
from .library import LibraryParser
from .longpoll import Longpoll
from .toolkit import ToolKit
from ..objects import exceptions
from ..objects.enums import LogLevel
from ..objects.data import Response
from ..utils import PATH_SEPARATOR, convert_to_package, toolkit_raise


class Bot:
    """
    Объект бота
    """

    def __init__(self, access_token, group_id, api_version = "5.531",
            assets_path: typing.Optional[str] = None, library_path: typing.Optional[str] = None,
            trust_env: bool = False) -> None:

        self.access_token = access_token
        self.group_id = group_id
        self.api_version = api_version

        self.assets_path = assets_path or os.getcwd() + PATH_SEPARATOR + "assets"
        self.library_path = library_path or os.getcwd() + PATH_SEPARATOR + "library"

        self._session = aiohttp.ClientSession(trust_env=trust_env)
        self.longpoll = Longpoll(self._session, self._method)
        self.toolkit = ToolKit(self._session, self._method, self.assets_path)
        self.library_parser = LibraryParser()


    def __repr__(self) -> str:
        return "<vkbotkit.framework.bot>"


    @property
    def api_url(self) -> str:
        """
        Прямой URL к API серверу ВКонтакте
        """

        return "https://api.vk.com/method/"


    async def _method(self, method: str = "groups.getById",
            params: typing.Optional[dict] = None) -> Response:
        """
        Скрытая функция для доступа к API
        """

        request_data = params or {}
        is_raw = request_data.pop("raw", False)

        if "access_token" not in request_data:
            request_data["access_token"] = self.access_token

        if "v" not in request_data:
            request_data["v"] = self.api_version

        response = await self._session.post(self.api_url + method, data = request_data)
        json = await response.json(content_type=None)

        if "response" in json:
            json = json['response']

        if isinstance(json, dict):
            if "error" in json:
                raise exceptions.MethodError(json["error"]["error_msg"])

            return json if is_raw else Response(json)

        if isinstance(json, list):
            return json if is_raw else list(map(Response, json))

        return json


    async def close(self) -> None:
        """
        Метод для безопасного закрытия сессии бота
        """

        loop = asyncio.get_event_loop()

        for task in asyncio.all_tasks(loop):
            task.cancel()

        await self._session.close()


    async def start_polling(self) -> None:
        """
        Начать обработку уведомлений с сервера ВКонтакте
        """

        self.library_parser.import_library(self.toolkit, self.library_path)

        if self.longpoll.is_polling:
            message = "polling already started"
            toolkit_raise(self.toolkit, message, LogLevel.ERROR, exceptions.LongpollError)

        loop = asyncio.get_event_loop()
        group_info = await self.toolkit.get_me()
        self.toolkit.group_id = group_info.id
        self.toolkit.screen_name = group_info.screen_name
        self.toolkit.is_polling = True

        await self.longpoll.update_server(self.toolkit.group_id)
        self.toolkit.log(f"longpoll started at @{self.toolkit.screen_name}")

        while self.toolkit.is_polling:
            for event in await self.longpoll.check(self.group_id):
                package = await convert_to_package(self.toolkit, event)
                parse_task = self.library_parser.parse(self.toolkit, package)
                loop.create_task(parse_task)

        await self.close()
