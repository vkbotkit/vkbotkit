"""
Copyright 2022 kensoi
"""

import typing
from . import enums
from . import data


class Filter:
    """
    Объект фильтра, помещаемый в декоратор vkbotkit.objects.decorators.callback
    """
    def __init__(self) -> None:
        self.priority = 0


    async def check(self, package) -> typing.Optional[bool]:
        """
        Пример проверки условий
        """

        package.toolkit.log(
            "Tried to use vkbotkit.objects.filters.Filter",
            log_level = enums.LogLevel.DEBUG
            )
        return True


    def __and__(self, other):
        assert issubclass(other.__class__, Filter)
        return AndF(self, other)


    def __or__(self, other):
        assert issubclass(other.__class__, Filter)
        return OrF(self, other)


    def __eq__(self, other):
        assert issubclass(other.__class__, Filter)
        return EqF(self, other)


    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} filter>"


class NotF(Filter):
    """
    Фильтр отрицания
    """
    def __init__(self, callback_filter) -> None:
        Filter.__init__(self)
        self.priority = 0
        if issubclass(callback_filter.__class__, Filter):
            self.__f = callback_filter
        else:
            raise TypeError("NotF filter should be initialized with filter object")

    async def check(self, package) -> typing.Optional[bool]:
        return not await self.__f.check(package)


class EqF(Filter):
    """
    Фильтр приравнивания фильтров
    """
    def __init__(self, a, b) -> None:
        Filter.__init__(self)
        self.priority = 0
        self.__a = a.check
        self.__b = b.check


    async def check(self, package) -> typing.Optional[bool]:
        return await self.__a(package) == await self.__b(package)


class AndF(Filter):
    """
    Оператор И для фильтров
    """
    def __init__(self, a, b) -> None:
        Filter.__init__(self)
        self.priority = 0
        assert issubclass(a.__class__, Filter)
        assert issubclass(b.__class__, Filter)
        self.__a = a.check
        self.__b = b.check


    async def check(self, package) -> typing.Optional[bool]:
        return await self.__a(package) and await self.__b(package)


class OrF(Filter):
    """
    Оператор ИЛИ для фильтров
    """
    def __init__(self, a, b) -> None:
        Filter.__init__(self)
        self.priority = 0
        assert issubclass(a.__class__, Filter)
        assert issubclass(b.__class__, Filter)
        self.__a = a.check
        self.__b = b.check


    async def check(self, package) -> typing.Optional[bool]:
        return await self.__a(package) or await self.__b(package)


class WhichUpdate(Filter):
    """
    Какого типа сообщения (vkbotkit.objects.enums.Events)
    """
    def __init__(self, types: typing.Union[list, set]):
        Filter.__init__(self)
        filteredtypes = filter(lambda update: isinstance(update, enums.Events), types)
        self.types = list(filteredtypes)
        self.priority = 0


    async def check(self, package) -> typing.Optional[bool]:
        return package.type in self.types


class IsForYou(Filter):
    """
    Содержит ли сообщение упоминания
    """
    def __init__(self, mentions):
        Filter.__init__(self)
        mapped_mentions = map(lambda x: str(x).lower(), mentions)
        self.mentions = set(mapped_mentions)
        self.update_type = WhichUpdate({enums.events.message_new})
        self.priority = 5
        self.bot_id = None
        self.group_id = None


    async def check(self, package):
        if await self.update_type.check(package):
            if len(package.items) >= 2:
                mention = package.items[0]
                if isinstance(mention, str) and mention.lower() in self.mentions:
                    return True

                elif isinstance(mention, data.mention):
                    if not self.group_id:
                        res = await package.toolkit.get_me()
                        self.bot_id = abs(res.id)

                    return self.bot_id == mention.id

class IsCommand(Filter):
    """
    Какая это команда
    """
    def __init__(self, commands):
        Filter.__init__(self)
        mapped_commands = map(lambda x: str(x).lower(), commands)
        self.commands = set(mapped_commands)
        self.update_type = WhichUpdate({enums.events.message_new})
        self.priority = 5


    async def check(self, package):
        if await self.update_type.check(package):
            if len(package.items) >= 2:
                return package.items[1] in self.commands

class HasPayload(Filter):
    """
    Payload from message
    """
    def __init__(self):
        Filter.__init__(self)
        self.update_type = WhichUpdate({enums.events.message_new})


    async def check(self, package) -> typing.Optional[bool]:
        if await self.update_type.check(package):
            return hasattr(package, "payload")
