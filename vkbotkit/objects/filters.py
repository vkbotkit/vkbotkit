"""
Copyright 2022 kensoi
"""

import typing
from . import enums
from .mention import Mention


class Filter:
    """
    Объект фильтра, помещаемый в декоратор vkbotkit.objects.decorators.callback
    """

    priority: int
    def __init__(self) -> None:
        self.priority = 0


    async def check(self, package) -> typing.Optional[bool]:
        """
        Пример проверки условий
        """

        package.toolkit.log("Tried to use <vkbotkit.objects.filters.Filter>",
            log_level = enums.LogLevel.DEBUG)
        return True


    def __and__(self, other):
        if issubclass(other.__class__, Filter):
            return AndF(self, other)

        raise TypeError(f"{repr(other.__class__)} should be subclass of Filter")


    def __or__(self, other):
        if issubclass(other.__class__, Filter):
            return OrF(self, other)

        raise TypeError(f"{repr(other.__class__)} should be subclass of Filter")


    def __eq__(self, other):
        if issubclass(other.__class__, Filter):
            return Equality(self, other)

        raise TypeError(f"{repr(other.__class__)} should be subclass of Filter")


    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} filter>"


class Negation(Filter):
    """
    Логическое отрицание для фильтров
    """

    def __init__(self, callback_filter) -> None:
        super().__init__()

        if not issubclass(callback_filter.__class__, Filter):
            raise TypeError(f"{repr(callback_filter.__class__)} should be subclass of Filter")

        self.__f = callback_filter


    async def check(self, package) -> typing.Optional[bool]:
        return not await self.__f.check(package)


class Equality(Filter):
    """
    Фильтр приравнивания фильтров
    """

    def __init__(self, first_filter, second_filter) -> None:
        if not issubclass(first_filter.__class__, Filter):
            raise TypeError(f"{repr(first_filter.__class__)} should be subclass of Filter")

        if not issubclass(second_filter.__class__, Filter):
            raise TypeError(f"{repr(second_filter.__class__)} should be subclass of Filter")

        super().__init__()

        self.first_filter = first_filter.check
        self.second_filter = second_filter.check


    async def check(self, package) -> typing.Optional[bool]:
        return await self.first_filter(package) == await self.second_filter(package)


class AndF(Filter):
    """
    Оператор И для фильтров
    """

    def __init__(self, first_filter, second_filter) -> None:
        if not issubclass(first_filter.__class__, Filter):
            raise TypeError(f"{repr(first_filter.__class__)} should be subclass of Filter")

        if not issubclass(second_filter.__class__, Filter):
            raise TypeError(f"{repr(second_filter.__class__)} should be subclass of Filter")

        super().__init__()

        self.first_filter = first_filter.check
        self.second_filter = second_filter.check


    async def check(self, package) -> typing.Optional[bool]:
        return await self.first_filter(package) and await self.second_filter(package)


class OrF(Filter):
    """
    Оператор ИЛИ для фильтров
    """

    def __init__(self, first_filter, second_filter) -> None:
        if not issubclass(first_filter.__class__, Filter):
            raise TypeError(f"{repr(first_filter.__class__)} should be subclass of Filter")

        if not issubclass(second_filter.__class__, Filter):
            raise TypeError(f"{repr(second_filter.__class__)} should be subclass of Filter")

        super().__init__()

        self.first_filter = first_filter.check
        self.second_filter = second_filter.check


    async def check(self, package) -> typing.Optional[bool]:
        return await self.first_filter(package) or await self.second_filter(package)


class WhichUpdate(Filter):
    """
    Какого типа сообщения (vkbotkit.objects.enums.Events)
    """

    def __init__(self, update_types: typing.Union[list, set]):
        super().__init__()
        self.types = list(filter(lambda update: isinstance(update, enums.Events), update_types))


    async def check(self, package) -> typing.Optional[bool]:
        return package.type in self.types


class IsForYou(Filter):
    """
    Содержит ли сообщение упоминания
    """
    def __init__(self, mentions, bot_id = None, group_id = None):
        self.mentions = set(map(lambda x: str(x).lower(), mentions))
        self.update_type = WhichUpdate({enums.Events.MESSAGE_NEW})
        self.bot_id = bot_id
        self.group_id = group_id

        super().__init__()
        self.priority = 5


    async def check(self, package):
        if not await self.update_type.check(package):
            return

        if len(package.items) < 2:
            return

        mention = package.items[0]

        if isinstance(mention, str) and mention.lower() in self.mentions:
            return True

        if not isinstance(mention, Mention):
            return

        if not self.group_id:
            res = await package.toolkit.get_me()
            self.bot_id = abs(res.id)

        return self.bot_id == mention.value


class IsCommand(Filter):
    """
    Какая это команда
    """

    def __init__(self, commands):
        self.commands = set(map(lambda x: str(x).lower(), commands))
        self.update_type = WhichUpdate({enums.Events.MESSAGE_NEW})

        super().__init__()
        self.priority = 5


    async def check(self, package):
        if not await self.update_type.check(package):
            return

        if len(package.items) < 2:
            return

        return package.items[1] in self.commands


class HasPayload(Filter):
    """
    Есть ли в сообщении данные из словаря
    """

    def __init__(self):
        self.update_type = WhichUpdate({enums.Events.MESSAGE_NEW})
        super().__init__()


    async def check(self, package) -> typing.Optional[bool]:
        if not await self.update_type.check(package):
            return

        return hasattr(package, "payload")


class NewUser(Filter):
    """
    Фильтр оповещений о новых участниках
    """

    async def check(self, package):
        if not package.action:
            return

        if not hasattr(package.action, "type"):
            return

        return package.action == "chat_invite_user"
