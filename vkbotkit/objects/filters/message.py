"""
Copyright 2022 kensoi
"""

import typing

from .filter import Filter
from ..package import Package
from ..enums import Events
from ..mention import Mention


init = lambda definition: definition()

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


@init
class HasBotMentions(Filter):
    """
    Содержит ли сообщение упоминания
    """

    async def check(self, toolkit, package: Package) -> typing.Optional[bool]:
        """
        Фильтрация обработчиков на условие
        """

        if package.type is not Events.MESSAGE_NEW:
            return
        
        if set(toolkit.bot_mentions) & set(package.items) != set():
            return True
        
        if int(await toolkit.get_my_mention()) in list(map(int, package.mentions)):
            return True
        
        return False


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

        if len(package.items) < 2:
            return
        
        elif len(package.items) == 2:
            if self.only_with_args:
                return
         
        elif len(package.items) > 2:
            if self.only_without_args:
                return
        
        if type(package.items[0]) == Mention:
            if int(package.items[0]) != int(await toolkit.get_my_mention()):
                return
        
        elif package.items[0].lower() not in toolkit.bot_mentions:
            return

        return package.items[1].lower() in self.commands


@init
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


@init
class IsUserChat(Filter):
    """
    Это диалог с пользователем?
    """

    async def check(self, _, package: Package) -> typing.Optional[bool]:
        if package.type is Events.MESSAGE_NEW:
            return package.peer_id == package.from_id


@init
class IsConversation(Filter):
    """
    Это диалог с пользователем?
    """

    async def check(self, _, package: Package) -> typing.Optional[bool]:
        if package.type is Events.MESSAGE_NEW:
            return package.peer_id != package.from_id


@init
class IsUserAdmin(Filter):
    """
    Проверка прав администратора у пользователя
    """

    async def check(self, toolkit, package: Package) -> typing.Optional[bool]:
        if package.type is Events.MESSAGE_NEW:
            response = await toolkit.is_admin(package.peer_id, package.from_id)
            return package.peer_id != package.from_id and response


@init
class IsBotAdmin(Filter):
    """
    Проверка прав администратора у пользователя
    """

    async def check(self, toolkit, package: Package) -> typing.Optional[bool]:
        if package.type is Events.MESSAGE_NEW:
            return package.peer_id != package.from_id and await toolkit.is_admin(package.peer_id)


@init
class GotReaction(Filter):
    async def check(self, _, package: Package) -> typing.Optional[bool]:
        if package.type is Events.MESSAGE_REACTION_EVENT:
            return "reaction_id" in package.raw
        
@init
class LostReaction(Filter):
    async def check(self, _, package: Package) -> typing.Optional[bool]:
        if package.type is Events.MESSAGE_REACTION_EVENT:
            return "reaction_id" not in package.raw
