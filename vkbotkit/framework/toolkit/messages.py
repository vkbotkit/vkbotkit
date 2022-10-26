"""
Copyright 2022 kensoi
"""

import typing
from .replies import Replies
from ...objects.package import Package
from ...utils import gen_random


class Messages:
    """
    Методы для работы с сообщениями
    """

    def __init__(self, api):
        self.__api = api
        self.replies = Replies()


    async def reply(self, package: Package, message: typing.Optional[str]=None,
            attachments: typing.Optional[str]=None,
            delete_last:bool = False, **kwargs):
        """
        Упрощённая форма отправки ответа
        """

        kwargs['peer_id'] = package.peer_id
        kwargs['message'] = message
        kwargs['attachments'] = attachments

        if  'random_id' not in kwargs:
            kwargs['random_id'] = gen_random()

        if delete_last:
            await self.delete(package)

        return await self.__api.messages.send(**kwargs)


    async def delete(self, package:Package):
        """
        Удалить сообщение
        """

        return await self.__api.messages.delete(
            conversation_message_ids = package.conversation_message_id,
            peer_id = package.peer_id, delete_for_all = 1)
