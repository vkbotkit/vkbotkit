import typing
from . import enums

class Filter:
    def __init__(self) -> None:
        self.priority = 0


    async def check(self, package) -> typing.Optional[bool]:
        return
        

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
    def __init__(self, filter) -> None:
        self.priority = 0
        if issubclass(filter.__class__, Filter):
            self.__F = filter
        else:
            raise TypeError("NotF filter should be initialized with filter object")

    async def check(self, package) -> typing.Optional[bool]:
        return not (await self.__F.check(package))


class EqF(Filter):
    def __init__(self, a, b) -> None:
        self.priority = 0
        self.__a = a.check
        self.__b = b.check


    async def check(self, package) -> typing.Optional[bool]:
        return await self.__a(package) == await self.__b(package)
        

class AndF(Filter):
    def __init__(self, a, b) -> None:
        self.priority = 0
        assert issubclass(a.__class__, Filter)
        assert issubclass(b.__class__, Filter)
        self.__a = a.check
        self.__b = b.check


    async def check(self, package) -> typing.Optional[bool]:
        return await self.__a(package) and await self.__b(package)


class OrF(Filter):
    def __init__(self, a, b) -> None:
        self.priority = 0
        assert issubclass(a.__class__, Filter)
        assert issubclass(b.__class__, Filter)
        self.__a = a.check
        self.__b = b.check


    async def check(self, package) -> typing.Optional[bool]:
        return await self.__a(package) or await self.__b(package)


class whichUpdate(Filter):
    def __init__(self, types: typing.Union[list, set]):
        filteredtypes = filter(lambda update: isinstance(update, enums.events), types)
        self.types = list(filteredtypes)
        self.priority = 0


    async def check(self, package) -> typing.Optional[bool]:
        return package.type in self.types
        

class isCommand(Filter):
    def __init__(self, commands: typing.Union[list, set]):
        mapped_commands = map(lambda x: str(x).lower(), commands)
        self.commands = set(mapped_commands)
        self.update_type = whichUpdate({enums.events.message_new})
        self.priority = 5


    async def check(self, package) -> typing.Optional[bool]:
        if await self.update_type.check(package):
            if len(package.commands) > 0:
                command = package.commands[0]
                if command.start == 0:
                    if command.command.lower() in self.commands:
                        return True


class havePayload():
    def __init__(self):
        self.update_type = whichUpdate({enums.events.message_new})
        

    async def check(self, package) -> typing.Optional[bool]:
        if await self.update_type.check(package):
            return hasattr(package, "payload")