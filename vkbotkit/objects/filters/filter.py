"""
Copyright 2022 kensoi
"""

from abc import abstractmethod
import typing
from ..package import Package

class Filter:
    """
    Объект фильтра, помещаемый в декоратор vkbotkit.objects.decorators.callback
    """

    priority: int
    def __init__(self) -> None:
        self.priority = 0


    @abstractmethod
    async def check(self, toolkit, package: Package) -> typing.Optional[bool]:
        """
        Пример проверки условий
        """


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


class Not(Filter):
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

        return not await self.filter_to_swap.check(toolkit, package)


class Equality(Filter):
    """
    Фильтр приравнивания фильтров
    """

    def __init__(self, first_filter, second_filter) -> None:
        super().__init__()
        self.check_filters(first_filter, second_filter)
        self.first_filter = first_filter
        self.second_filter = second_filter


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

        response_first = await self.first_filter.check(toolkit, package)
        response_second = await self.second_filter.check(toolkit, package)

        return response_first == response_second


class AndF(Filter):
    """
    Оператор И для фильтров
    """

    def __init__(self, first_filter, second_filter) -> None:
        super().__init__()
        self.check_filters(first_filter, second_filter)
        self.first_filter = first_filter
        self.second_filter = second_filter


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

        response_first = await self.first_filter.check(toolkit, package)
        response_second = await self.second_filter.check(toolkit, package)

        return response_first and response_second


class OrF(Filter):
    """
    Оператор ИЛИ для фильтров
    """

    def __init__(self, first_filter, second_filter) -> None:
        super().__init__()
        self.check_filters(first_filter, second_filter)
        self.first_filter = first_filter
        self.second_filter = second_filter


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

        if not await self.first_filter.check(toolkit, package):
            return await self.second_filter.check(toolkit, package)

        return True
