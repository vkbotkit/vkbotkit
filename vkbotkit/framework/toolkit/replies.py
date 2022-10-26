"""
Copyright 2022 kensoi
"""

import asyncio
import time


class Replies:
    """
    Система ожидания ответа в переписке
    """

    def __init__(self) -> None:
        self.__task_list = {}


    def __repr__(self) -> str:
        return "<vkbotkit.framework.toolkit.replies>"


    def check(self, package):
        """
        Специальная функция для получения новых оповещений с беседы.
        """

        for message_task in self.__task_list.values():
            if message_task.peer_id == package.peer_id:
                if message_task.from_id == package.from_id:
                    message_task.response = package
                    return True


    async def get(self, package):
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
        self.from_id = package.from_id
        self.response = None


    def __repr__(self) -> str:
        return "<vkbotkit.framework.toolkit.replies.task>"


    def __str__(self):
        return f"${self.timestamp}_{self.peer_id}_{self.from_id}"
