"""
Copyright 2022 kensoi
"""

import typing
from .filter import Filter
from ..data import Package


class ChatInviteUser(Filter):
    """
    Фильтр оповещений о новых участниках
    """

    async def check(self, package: Package) -> typing.Optional[bool]:
        """
        Фильтрация обработчиков на условие
        """

        if self.check_action(package):
            return package.action == "chat_invite_user"


    def check_action(self, package):
        """
        Проверка сообщения на событийность
        """

        if package.action:
            return hasattr(package.action, "type")
