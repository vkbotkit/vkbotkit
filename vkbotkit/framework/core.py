"""
Copyright 2022 kensoi
"""

import asyncio
import logging

import aiohttp

from .features import GetAPI, Longpoll
from ..objects import exceptions, data

logger = logging.getLogger("VKBotKit")

class Core:
    """
    Ядро бота
    """

    def __init__(self, token):
        self.__token = token
        self.__v = "5.131"

        self.session = aiohttp.ClientSession(trust_env=True)
        self.longpoll = Longpoll(self.session, self._method)


    def close(self):
        """
        закрытие
        """
        loop = asyncio.get_event_loop()
        loop.create_task(self.session.close())


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
            request_data["access_token"] = self.__token

        if "v" not in request_data:
            request_data["v"] = self.__v

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


    def __repr__(self):
        return "<vkbotkit.Core>"
