"""
Copyright 2023 kensoi
"""

import typing
from .api import GetAPI
from .assets import Assets
from .messages import Messages
from .uploader import Uploader
from .logger import Log
from ...objects import data, exceptions, enums
from ...objects.mention import Mention


class ToolKit:
    """
    Инструментарий
    """

    def __init__ (self, bot):
        self.session = bot.session
        self.method = bot.method

        self.bot_id:bool = None
        self.screen_name:bool = None
        self.bot_is_group:bool = None

        self.assets = Assets(self)
        self.log = Log()
        self.messages = Messages(self.api)
        self.upload = Uploader(self.assets, self.api)
        self.is_polling = False
        self.bot_mentions = []

    def __repr__(self):
        return "<vkbotkit.framework.toolkit>"

    @property
    def api(self):
        """
        Обёртка вокруг Bot._method()
        """

        return GetAPI(self.session, self.method)

    async def match_data(self):
        """
        set basic data about bot
        """

        bot_data = await self.get_me(fields="screen_name")

        self.bot_id = bot_data.id
        self.screen_name = bot_data.screen_name
        self.bot_is_group = bot_data.raw.get("type") == "group"

    def stop_polling(self) -> None:
        """
        Остановить обработку уведомлений с сервера
        """

        if not self.is_polling:
            self.log(
                "attempt to stop poll cycle that is not working now",
                enums.LogLevel.WARNING)
            return

        self.is_polling = False

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

        users_info = await self.api.users.get(fields = fields)

        if len(users_info) == 0:
            communities_info = await self.api.groups.getById(fields = fields)
            return communities_info.groups[0]

        return users_info[0]


    async def get_my_mention(self) -> Mention:
        """
        Получить форму упоминания сообщества, в котором работает ваш бот
        """

        return await self.create_mention(
            self.bot_id * (-1 * self.bot_is_group),
            f"@{self.screen_name}"
        )

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

    async def get_community_admins(self, community):
        """
        Получить список ID участников, кто является администратором.

        Возвращает список объектов со свойствами id [int], permissions [list] и role [str]

        Если функция вернула пустой список, то бот не имеет прав администратора в этом сообществе   
        """

        try:
            response = await self.api.groups.getMembers(
                group_id = community,
                filter = "managers"
            )

            return response.items

        except exceptions.MethodError as method_error:
            self.log(str(method_error), enums.LogLevel.DEBUG)
            return []

    async def get_bot_admins(self):
        """
        Получить список ID участников, кто является администратором в сообществе, 
        где установлен бот.
        """

        if not self.bot_is_group:
            self.log("Your bot is not community. It is user", enums.LogLevel.ERROR)
            raise exceptions.MethodError("Your bot is not community. It is user")

        return await self.get_community_admins(self.bot_id)
