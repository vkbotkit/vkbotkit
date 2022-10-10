"""
Copyright 2022 kensoi
"""

import asyncio
import logging
import os
import random
import typing

import aiohttp

from .framework.longpoll import Longpoll
from .framework.api import GetAPI
from .framework.features import Assets, CallbackLib, Logger, Uploader
from .framework.replies import Replies
from .framework.utils import PATH_SEPARATOR, Mention, dump_mention

from .objects import data, exceptions, enums, keyboard
from .objects import NAME_CASES

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


class ToolKit:
    """
    Инструментарий
    """

    def __init__ (self, token, group_id = None, assets_path = None):
        self.__logger = None
        self.assets = Assets(self, assets_path)
        self.group_id = group_id
        self.core = Core(token)
        self.replies = Replies()
        self.uploader = Uploader(self)
        self.__poll_task = None
        self.__event_loop = asyncio.get_event_loop()


    def __repr__(self):
        return "<vkbotkit.ToolKit>"


    def close(self):
        """
        Закрыть инструменты безопасно
        """
        if self.__poll_task:
            self.__poll_task.cancel()

        self.core.close()

        for task in asyncio.all_tasks(self.__event_loop):
            task.cancel()

        print(">> Done closing tasks")


    @property
    def api(self) -> GetAPI:
        """
        Получить обёртку для VK API
        """
        return self.core.api


    async def start_polling(self, library:typing.Optional[CallbackLib] = None) -> None:
        """
        Начать обработку уведомлений
        """

        if not library:
            raise Exception("You should connect a library here")

        if len(library.handlers) == 0:
            library.import_library(self)

        if self.core.longpoll.is_polling:
            self.log("polling already started", log_level=enums.LogLevel.ERROR)
            raise Exception("polling already started")

        self.core.longpoll.is_polling = True
        group_info = await self.get_me()
        await self.core.longpoll.update_server(group_info.id)
        self.log(f"longpoll started at @{group_info.screen_name}")

        while self.core.longpoll.is_polling:
            map(lambda event: self.__event_loop.create_task(library.parse(self, event)),
                await self.core.longpoll.check(group_info.id))

        self.close()


    def is_polling(self) -> bool:
        """
        Работает ли в данный момент поллинг.
        """

        return self.core.longpoll.is_polling


    def stop_polling(self) -> None:
        """
        Остановить обработку уведомлений с сервера
        """

        if self.core.longpoll.is_polling:
            self.core.longpoll.is_polling = False
            self.log("polling finished", enums.LogLevel.DEBUG)

        else:
            self.log(
                "attempt to stop poll cycle that is not working now",
                enums.LogLevel.WARNING)


    def configure_logger(self, log_level: enums.LogLevel = enums.LogLevel.INFO,
        log_to_file = False, log_to_console = False):
        """
        Настроить логгер
        """

        self.__logger = Logger("vkbotkit", log_level, log_to_file, log_to_console)


    def log(self, message,
        log_level: enums.LogLevel = enums.LogLevel.INFO) -> None:
        """
        Записать сообщение в логгер
        """

        if self.__logger:
            self.__logger.log(message, log_level)


    def gen_random(self) -> int:
        """
        Сгенерировать случайное число (для messages.send метода)
        """

        return int(random.random() * 999999)


    def create_keyboard(self, one_time: bool=False, inline: bool=False) -> keyboard.Keyboard:
        """
        Создать клавиатуру
        """

        return keyboard.Keyboard(one_time, inline)


    async def get_me(self, fields=None) -> data.Response:
        """
        Получить информацию о сообществе, в котором работает ваш бот
        """

        if not fields:
            fields = ['screen_name']

        page_info = await self.api.users.get(fields=', '.join(fields), raw=True)

        if len(page_info) > 0:
            bot_type = "id"

        else:
            page_info = await self.api.groups.getById(fields = ", ".join(fields), raw=True)

            if len(page_info) > 0:
                bot_type = "club"

        return data.Response({
            **page_info[0], "bot_type": bot_type
        })


    async def get_my_mention(self) -> Mention:
        """
        Получить форму упоминания сообщества, в котором работает ваш бот
        """

        res = await self.get_me()
        return dump_mention(f"[{res.bot_type + str(res.id)}|{res.screen_name}]")


    async def send_reply(
        self, package: data.Package, message: typing.Optional[str]=None,
        attachment: typing.Optional[str]=None,
        delete_last:bool = False, **kwargs):
        """
        Упрощённая форма отправки ответа
        """

        if  'peer_id' not in kwargs:
            kwargs['peer_id'] = package.peer_id

        if  'random_id' not in kwargs:
            kwargs['random_id'] = self.gen_random()

        if  'message' not in kwargs and message:
            kwargs['message'] = message

        if  'attachment' not in kwargs and attachment:
            kwargs['attachment'] = attachment

        if delete_last:
            await self.delete_message(package)

        return await self.api.messages.send(**kwargs)


    async def delete_message(self, package):
        """
        Удалить сообщение
        """

        return await self.api.messages.delete(
            conversation_message_ids = package.conversation_message_id,
            peer_id = package.peer_id, delete_for_all = 1)


    async def get_chat_members(self, peer_id):
        """
        Получить список участников в беседе
        """

        chat_list = await self.api.messages.getConversationMembers(peer_id = peer_id)
        members = list(map(lambda x: x.member_id, chat_list.items))
        return members


    async def get_chat_admins(self, peer_id):
        """
        Получить список администраторов в беседе
        """

        chat_list = await self.api.messages.getConversationMembers(peer_id = peer_id)

        members_mapped = map(lambda x: x.member_id if hasattr(x, "is_admin") else None,
                    chat_list.items)
        members_filtered = list(filter(lambda x: x is not None, members_mapped))

        return members_filtered


    async def is_admin(self, peer_id: int, user_id: typing.Optional[int] = None):
        """
        Проверяет наличие прав у пользователя
        Если user_id пустой -- проверяется наличие прав у бота
        """
        if not user_id:
            try:
                admin_list = await self.get_chat_admins(peer_id)
                return True

            except exceptions.MethodError:
                return False

        admin_list = await self.get_chat_admins(peer_id)
        return user_id in admin_list


    async def create_mention(self, mention_id: int,mention_key: typing.Optional[str] = None,
        name_case: typing.Optional[str] = None):
        """
        Создать упоминание
        """

        if not mention_key:
            if mention_id > 0:
                if name_case:
                    if hasattr(enums.NameCases, name_case):
                        pass

                    else:
                        name_case = enums.NameCases.NOM

                else:
                    name_case = NAME_CASES[0]

                response = await self.api.users.get(user_ids = mention_id, name_case = name_case)
                mention_key = response[0].first_name

            else:
                response = await self.api.groups.getById(group_id = mention_id)
                mention_key = response[0].name

        return Mention(mention_id, mention_key)


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
