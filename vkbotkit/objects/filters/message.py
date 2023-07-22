"""
Copyright 2022 kensoi
"""

import typing

from .filter import Filter
from ..package import Package
from ..enums import Events
from ..mention import Mention


class IsThatText(Filter):
    """
    Отправил ли пользователь точно такое же сообщение
    """

    def __init__(self, messages_to_compare: str) -> None:
        super().__init__()
        self.messages_to_compare = messages_to_compare


    async def check(self, _, package: Package) -> typing.Optional[bool]:
        """
        Фильтрация обработчиков на условие
        """

        if package.type is Events.MESSAGE_NEW:
            return package.text in self.messages_to_compare


class IsForBot(Filter):
    """
    Содержит ли сообщение упоминания
    """

    def __init__(self, mentions, group_id = None):
        super().__init__()

        self.mentions = set(map(lambda x: str(x).lower(), mentions))
        self.group_id = group_id
        self.priority = 5


    async def check(self, toolkit, package: Package) -> typing.Optional[bool]:
        """
        Фильтрация обработчиков на условие
        """

        if package.type is not Events.MESSAGE_NEW:
            return

        mention = package.items[0]

        if isinstance(mention, str) and mention.lower() in self.mentions:
            return True

        if not isinstance(mention, Mention):
            return

        if not self.group_id:
            self.group_id = toolkit.group_id

        return self.group_id == mention.value


class IsCommand(Filter):
    """
    Какая это команда
    """

    def __init__(self, commands, only_with_args=False, only_without_args=False):
        super().__init__()

        self.commands = set(map(lambda x: str(x).lower(), commands))
        self.priority = 5 
        self.only_with_args = only_with_args
        self.only_without_args = only_without_args

    async def check(self, toolkit, package: Package) -> typing.Optional[bool]:
        """
        Фильтрация обработчиков на условие
        """

        if package.type is not Events.MESSAGE_NEW:
            return

        elif len(package.items) < 2:
            return
        
        elif len(package.items) == 2:
            if self.only_with_args:
                return
         
        elif len(package.items) > 2:
            if self.only_without_args:
                return
        
        elif type(package.items[0]) == Mention:
            if int(package.items[0]) != int(await toolkit.get_my_mention()):
                return
        
        elif package.items[0].lower() not in toolkit.bot_mentions:
            return

        return package.items[1].lower() in self.commands


class HasPayload(Filter):
    """
    Есть ли в сообщении данные из словаря
    """

    async def check(self, _, package: Package) -> typing.Optional[bool]:
        """
        Фильтрация обработчиков на условие
        """

        if package.type is Events.MESSAGE_NEW:
            return hasattr(package, "payload")


class IsUserChat(Filter):
    """
    Это диалог с пользователем?
    """

    async def check(self, _, package: Package) -> typing.Optional[bool]:
        if package.type is Events.MESSAGE_NEW:
            return package.peer_id == package.from_id


class IsConversation(Filter):
    """
    Это диалог с пользователем?
    """

    async def check(self, _, package: Package) -> typing.Optional[bool]:
        if package.type is Events.MESSAGE_NEW:
            return package.peer_id != package.from_id


class IsUserAdmin(Filter):
    """
    Проверка прав администратора у пользователя
    """

    async def check(self, toolkit, package: Package) -> typing.Optional[bool]:
        if package.type is Events.MESSAGE_NEW:
            response = await toolkit.is_admin(package.peer_id, package.from_id)
            return package.peer_id != package.from_id and response


class IsBotAdmin(Filter):
    """
    Проверка прав администратора у пользователя
    """

    async def check(self, toolkit, package: Package) -> typing.Optional[bool]:
        if package.type is Events.MESSAGE_NEW:
            return package.peer_id != package.from_id and await toolkit.is_admin(package.peer_id)
