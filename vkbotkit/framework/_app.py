"""
Copyright 2022 kensoi
"""
import asyncio
import os
import random
import typing
from . import _features, _api
from .. import objects
from ..objects.data import Response


class Toolkit:
    """
    Инструментарий
    """

    def __init__ (self, token, assets_path = None):
        """
        docstring patch
        """

        self.__logger = None
        self.assets = _features.Assets(self, assets_path)
        self.core = _api.Core(token)
        self.replies = _features.Replies()
        self.uploader = _api.Uploader(self)

    @property
    def __event_loop(self):
        """
        docstring patch
        """

        return asyncio.get_event_loop()


    @property
    def api(self) -> _api.API:
        """
        docstring patch
        """

        return self.core._api


    async def start_polling(
        self, library:typing.Optional[_features.CallbackLib] = None
        ) -> None: # only for group bots
        """
        Начать обработку уведомлений
        """

        if not library:
            raise Exception("You should connect a library here")

        if self.core._longpoll._is_polling:
            self.log("polling already started", log_level=objects.enums.log_level.ERROR)
            raise Exception("polling already started")

        self.core._longpoll._is_polling = True
        group_info = await self.api.groups.getById()
        await self.core._longpoll._Longpoll__update_longpoll_server(group_info[0].id)
        
        self.log(f"[{group_info[0].screen_name}] polling is started")

        while self.core._longpoll._is_polling:
            for event in await self.core._longpoll._check(group_info[0].id):
                self.__event_loop.create_task(library.parse(self, event))

    def is_polling(self) -> bool:
        """
        Работает ли в данный момент поллинг.
        """

        return self.core._longpoll._is_polling


    def stop_polling(self) -> None:
        """
        Остановить обработку уведомлений с сервера
        """

        if self.core._longpoll._is_polling:
            self.core._longpoll._is_polling = False
            self.log("polling finished", objects.enums.log_level.DEBUG)

        else:
            self.log(
                "attempt to stop poll cycle that is not working now",
                objects.enums.LogLevel.WARNING)


    def configure_logger(
        self, log_level: objects.enums.LogLevel = objects.enums.LogLevel.INFO,
        file_log = False, print_log = False
        ):
        """
        Настроить логгер
        """

        self.__logger = _features.Logger("vkbotkit", log_level, file_log, print_log)


    def log(
        self, message,
        log_level: objects.enums.LogLevel = objects.enums.LogLevel.INFO) -> None:
        """
        Записать сообщение в логгер
        """

        if self.__logger:
            self.__logger.logger.log(level = log_level.value, msg = message)


    def gen_random(self) -> int:
        """
        Сгенерировать случайное число (для messages.send метода)
        """

        return int(random.random() * 999999)


    def create_keyboard(self, one_time:bool=False, inline:bool=False) -> objects.keyboard.Keyboard:
        """
        Создать клавиатуру
        """

        return objects.keyboard.Keyboard(one_time, inline)


    async def get_me(self, fields=None) -> Response:
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

        return Response({
            **page_info[0], "bot_type": bot_type
        })


    async def get_my_mention(self) -> objects.data.Mention:
        """
        Получить форму упоминания сообщества, в котором работает ваш бот
        """

        res = await self.get_me()
        return objects.data.Mention(f"[{res.bot_type + str(res.id)}|{res.screen_name}]")


    async def send_reply(
        self, package: objects.data.Package, message: typing.Optional[str]=None,
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

        chat_list = await self.api.messages.getConversationMembers(
            peer_id = peer_id)

        members = list(map(lambda x: x.member_id, chat_list.items))

        return members

    async def get_chat_admins(self, peer_id):
        """
        Получить список администраторов в беседе
        """

        chat_list = await self.api.messages.getConversationMembers(
            peer_id = peer_id)

        members = map(
                    lambda x: x.member_id if hasattr(x, "is_admin") else None,
                    chat_list.items
                    )
        members = list(filter(lambda x: x is not None, members))

        return members



class Librabot:
    """
    Объект бота
    """

    def __init__(self, token, assetpath = None, libpath = None):
        """
        docstring patch
        """

        if not assetpath:
            assetpath = os.getcwd() + objects.PATH_SEPARATOR + "assets"

        if not libpath:
            libpath = os.getcwd() + objects.PATH_SEPARATOR + "library"

        self.toolkit = Toolkit(token, assetpath)
        self.library = _features.CallbackLib(self.toolkit, libpath)


    async def start_polling(self) -> None:
        """
        Начать обработку уведомлений с сервера ВКонтакте
        """

        await self.toolkit.start_polling(self.library)
