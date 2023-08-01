"""
Copyright 2023 kensoi
"""

import typing
import aiohttp
from aiohttp.client_exceptions import ClientConnectorError

from .longpoll import BotLongpoll
from .toolkit  import ToolKit
from ..objects import exceptions
from ..objects.enums import LogLevel
from ..objects.data import Response

from ..utils import convert_to_package


class Bot:
    """
    Объект бота
    """

    def __init__(self, access_token, bot_id, api_version = "5.531",
            trust_env: bool = False) -> None:
        self.access_token = access_token
        self.bot_id = bot_id
        self.api_version = api_version

        self.session = aiohttp.ClientSession(trust_env=trust_env)
        self.toolkit = ToolKit(self)
        self.longpoll = BotLongpoll(self)

    def __repr__(self) -> str:
        return "<vkbotkit.framework.bot>"

    @property
    def api_url(self) -> str:
        """
        Прямой URL к API серверу ВКонтакте
        """

        return "https://api.vk.com/method/"

    async def method(self, method: str = "groups.getById",
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

        response = await self.session.post(self.api_url + method, data = request_data)
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

    async def poll_server(self):
        """
        get updates from server
        """
        await self.toolkit.match_data()

        await self.longpoll.update_server(self.toolkit.bot_id)
        self.toolkit.is_polling = True
        self.toolkit.log(f"@{self.toolkit.screen_name}: started polling.")

        try:
            while self.toolkit.is_polling:
                for event in await self.longpoll.check(self.bot_id):
                    yield convert_to_package(self.toolkit, event)

        except ClientConnectorError as error_object:
            self.toolkit.log(f"ClientConnectorError: {error_object}", log_level=LogLevel.ERROR)

        finally:
            self.toolkit.log(f"@{self.toolkit.screen_name}: stopped polling.")
