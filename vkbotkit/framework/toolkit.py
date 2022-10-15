"""
Copyright 2022 kensoi
"""

import asyncio
import typing
import random

from .core import Core

from .features import GetAPI, Assets, Replies, Uploader, Logger, CallbackLib
from ..objects import data, exceptions, enums, keyboard, NAME_CASES
from ..utils import Mention, dump_mention


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
            for event in await self.core.longpoll.check(group_info.id):
                self.__event_loop.create_task(library.parse(self, event))

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
