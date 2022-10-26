"""
Copyright 2022 kensoi
"""

import typing
from .filter import Filter
from ..package import Package


class Negation(Filter):
    """
    Логическое отрицание для фильтров
    """

    def __init__(self, filter_to_swap) -> None:
        super().__init__()
        self.check_filter(filter_to_swap)
        self.filter_to_swap = filter_to_swap


    def check_filter(self, filter_to_swap):
        """
        Проверка валидности фильтра
        """

        if not issubclass(filter_to_swap.__class__, Filter):
            raise TypeError(f"{repr(filter_to_swap.__class__)} should be subclass of Filter")


    async def check(self, toolkit, package: Package) -> typing.Optional[bool]:
        """
        Фильтрация обработчиков на условие
        """

        return not await self.filter_to_swap.check(package)


class Equality(Filter):
    """
    Фильтр приравнивания фильтров
    """

    def __init__(self, first_filter, second_filter) -> None:
        super().__init__()
        self.check_filters(first_filter, second_filter)
        self.first_filter = first_filter.check
        self.second_filter = second_filter.check


    def check_filters(self, first_filter, second_filter):
        """
        Проверка валидности фильтров
        """

        if not issubclass(first_filter.__class__, Filter):
            raise TypeError(f"{repr(first_filter.__class__)} should be subclass of Filter")

        if not issubclass(second_filter.__class__, Filter):
            raise TypeError(f"{repr(second_filter.__class__)} should be subclass of Filter")


    async def check(self, toolkit, package: Package) -> typing.Optional[bool]:
        """
        Фильтрация обработчиков на условие
        """

        return await self.first_filter(package) == await self.second_filter(package)


class AndF(Filter):
    """
    Оператор И для фильтров
    """

    def __init__(self, first_filter, second_filter) -> None:
        super().__init__()
        self.check_filters(first_filter, second_filter)
        self.first_filter = first_filter.check
        self.second_filter = second_filter.check


    def check_filters(self, first_filter, second_filter):
        """
        Проверка валидности фильтров
        """

        if not issubclass(first_filter.__class__, Filter):
            raise TypeError(f"{repr(first_filter.__class__)} should be subclass of Filter")

        if not issubclass(second_filter.__class__, Filter):
            raise TypeError(f"{repr(second_filter.__class__)} should be subclass of Filter")


    async def check(self, toolkit, package: Package) -> typing.Optional[bool]:
        """
        Фильтрация обработчиков на условие
        """

        return await self.first_filter(package) and await self.second_filter(package)


class OrF(Filter):
    """
    Оператор ИЛИ для фильтров
    """

    def __init__(self, first_filter, second_filter) -> None:
        super().__init__()
        self.check_filters(first_filter, second_filter)
        self.first_filter = first_filter.check
        self.second_filter = second_filter.check


    def check_filters(self, first_filter, second_filter):
        """
        Проверка валидности фильтров
        """

        if not issubclass(first_filter.__class__, Filter):
            raise TypeError(f"{repr(first_filter.__class__)} should be subclass of Filter")

        if not issubclass(second_filter.__class__, Filter):
            raise TypeError(f"{repr(second_filter.__class__)} should be subclass of Filter")


    async def check(self, toolkit, package: Package) -> typing.Optional[bool]:
        """
        Фильтрация обработчиков на условие
        """

        return await self.first_filter(package) or await self.second_filter(package)
