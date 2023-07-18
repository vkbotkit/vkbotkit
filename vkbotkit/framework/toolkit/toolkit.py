"""
Copyright 2022 kensoi
"""

import typing
from .api import GetAPI
from .assets import Assets
from .messages import Messages
from .uploader import Uploader
from .logger import Log
from ...objects import data, exceptions, enums
from ...objects.mention import Mention
from ...utils import dump_mention


class ToolKit:
    """
    Инструментарий
    """

    def __init__ (self, session, method, assets_path = None):
        self._session = session
        self._method = method

        self.assets = Assets(self, assets_path)
        self.log = Log()
        self.messages = Messages(self.api)
        self.upload = Uploader(self.assets, self.api)
        self.is_polling = False


    def __repr__(self):
        return "<vkbotkit.framework.toolkit>"

    @property
    def api(self):
        """
        Обёртка вокруг Bot._method()
        """

        return GetAPI(self._session, self._method)


    def stop_polling(self) -> None:
        """
        Остановить обработку уведомлений с сервера
        """

        if self.is_polling:
            self.is_polling = False
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

        self.log.configure("vkbotkit", log_level, log_to_file, log_to_console)


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
            **page_info['groups'][0], "bot_type": bot_type
        })


    async def get_my_mention(self) -> Mention:
        """
        Получить форму упоминания сообщества, в котором работает ваш бот
        """

        res = await self.get_me()
        return dump_mention(f"[{res.bot_type + str(res.id)}|{res.screen_name}]")


    async def get_chat_members(self, peer_id):
        """
        Получить список участников в беседе
        """

        conversation_members = await self.api.messages.getConversationMembers(peer_id = peer_id)
        return list(map(lambda x: x.member_id, conversation_members.items))


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

        if user_id:
            return user_id in await self.get_chat_admins(peer_id)

        try:
            await self.get_chat_admins(peer_id)

        except exceptions.MethodError:
            return False

        else:
            return True


    async def create_mention(self, mention_id: int,
        mention_key: typing.Optional[str] = None,
        name_case: typing.Optional[enums.NameCases] = enums.NameCases.NOM):
        """
        Создать упоминание
        """

        if not mention_key:
            if int(mention_id) > 0:
                response = await self.api.users.get(
                    user_ids = mention_id, name_case = name_case.value)
                mention_key = response[0].first_name

            else:
                response = await self.api.groups.getById(group_id = mention_id)
                mention_key = response[0].name

        return Mention(mention_id, mention_key)
