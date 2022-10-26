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
            return self and other

        raise TypeError(f"{repr(other.__class__)} should be subclass of Filter")


    def __or__(self, other):
        if issubclass(other.__class__, Filter):
            return self and other

        raise TypeError(f"{repr(other.__class__)} should be subclass of Filter")


    def __eq__(self, other):
        if issubclass(other.__class__, Filter):
            return self and other

        raise TypeError(f"{repr(other.__class__)} should be subclass of Filter")


    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} filter>"
