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

    def __init__(self, message_to_compare: str) -> None:
        super().__init__()
        self.message_to_compare = message_to_compare


    async def check(self, toolkit, package: Package) -> typing.Optional[bool]:
        """
        Фильтрация обработчиков на условие
        """

        if package.type is Events.MESSAGE_NEW:
            return package.text == self.message_to_compare


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

    def __init__(self, commands):
        super().__init__()

        self.commands = set(map(lambda x: str(x).lower(), commands))
        self.priority = 5


    async def check(self, toolkit, package: Package) -> typing.Optional[bool]:
        """
        Фильтрация обработчиков на условие
        """

        if package.type is not Events.MESSAGE_NEW:
            return

        if len(package.items) < 2:
            return

        return package.items[1] in self.commands


class HasPayload(Filter):
    """
    Есть ли в сообщении данные из словаря
    """

    async def check(self, toolkit, package: Package) -> typing.Optional[bool]:
        """
        Фильтрация обработчиков на условие
        """

        if package.type is Events.MESSAGE_NEW:
            return hasattr(package, "payload")
