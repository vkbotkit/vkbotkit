"""
Copyright 2023 kensoi
"""

import asyncio
import time
import typing
from ...objects.package import Package
from ...utils import gen_random


class Messages:
    """
    Методы для работы с сообщениями
    """

    def __init__(self, api):
        self.__api = api
        self.__task_list = {}


    async def send(self, package: Package, message: typing.Optional[str]=None,
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


    def check_for_waiting_reply(self, package):
        """
        Специальная функция для получения новых оповещений с беседы.
        """

        for message_task in self.__task_list.values():
            if "peer_id" not in package.raw:
                continue

            if message_task.peer_id == package.peer_id:
                if message_task.from_id == package.from_id:
                    message_task.response = package
                    return True


    async def get_reply(self, package):
        """
        Специальная функция для получения новых оповещений с беседы.
        """

        message_task = ReplyTask(package)
        self.__task_list[str(message_task)] = message_task

        while not message_task.response:
            await asyncio.sleep(0.01)

        self.__task_list.pop(str(message_task), None)

        return message_task.response


class ReplyTask:
    """
    Объект задачи для ожидания ответа
    """

    def __init__(self, package):
        self.timestamp = time.time()
        self.peer_id = package.peer_id

        if "from_id" in package.raw:
            self.from_id = package.from_id  

        else:
            self.from_id = package.peer_id

        self.response = None


    def __repr__(self) -> str:
        return "<vkbotkit.framework.toolkit.replies.task>"


    def __str__(self):
        return f"${self.timestamp}_{self.peer_id}_{self.from_id}"
