"""
Copyright 2022 kensoi
"""

import typing
from .filter import Filter
from ..data import Package
from ..enums import Events


class WhichEvent(Filter):
    """
    Какого типа сообщения (vkbotkit.objects.enums.Events)
    """

    def __init__(self, events: typing.Union[list[Events], set[Events]]):
        super().__init__()
        self.filter_events(events)
        self.events = events


    def filter_events(self, events: list) -> bool:
        """
        Проверка списка
        """

        events_filtered = list(filter(lambda event: isinstance(event, Events), events))
        return events == events_filtered


    async def check(self, package: Package) -> typing.Optional[bool]:
        """
        Фильтрация обработчиков на условие
        """

        return package.type in self.events
