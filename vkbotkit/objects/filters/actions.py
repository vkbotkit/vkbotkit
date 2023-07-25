"""
Copyright 2023 kensoi
"""

import typing
from .filter import Filter
from ..enums import Action as ActionEnum, Events
from ..package import Package

init = lambda definition: definition()

class Action(Filter):
    """
    Фильтр оповещений о новых участниках
    """
    action: ActionEnum


    def check_action(self, package):
        """
        Проверка сообщения на событийность
        """

        return hasattr(package, "action")


    async def check(self, _, package: Package) -> typing.Optional[bool]:
        """
        Фильтрация обработчиков на условие
        """

        if package.type is Events.MESSAGE_NEW:
            if self.check_action(package):
                return package.action.type is self.action

@init
class ChatPhotoUpdate(Action):
    """
    Обновление аватарки чата
    """

    action = ActionEnum.CHAT_PHOTO_UPDATE


@init
class ChatPhotoRemove(Action):
    """
    Аватарка удалена
    """

    action = ActionEnum.CHAT_PHOTO_REMOVE


@init
class ChatCreate(Action):
    """
    Создан чат
    """

    action = ActionEnum.CHAT_CREATE


@init
class ChatTitleUpdate(Action):
    """
    Изменено название чата
    """

    action = ActionEnum.CHAT_TITLE_UPDATE


@init
class ChatInviteUser(Action):
    """
    Приглашён пользователь
    """

    action = ActionEnum.CHAT_INVITE_USER


@init
class ChatKickUser(Action):
    """
    Исключён пользователь
    """

    action = ActionEnum.CHAT_KICK_USER


@init
class ChatPinMessage(Action):
    """
    Прикреплено сообщение
    """

    action = ActionEnum.CHAT_PIN_MESSAGE


@init
class ChatUnpinMessage(Action):
    """
    Откреплено сообщение
    """

    action = ActionEnum.CHAT_UNPIN_MESSAGE


@init
class ChatInviteUserByLink(Action):
    """
    Пользователь вступил в чат с помощью ссылки
    """

    action = ActionEnum.CHAT_INVITE_USER_BY_LINK
