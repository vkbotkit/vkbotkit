"""
Copyright 2022 kensoi
"""

import asyncio


class Handler():
    """
    Класс обработчика события
    """

    def __init__(self, lib_filter, lib_callback, module):
        self.filter = lib_filter
        self.callback = lib_callback
        self.module = module


    def __repr__(self):
        return "<vkbotkit.framework.handler.Handler>"


    @property
    def loop(self):
        """
        Цикл обработчика внутри потока
        """

        return asyncio.get_event_loop()


    async def create_task(self, package):
        """
        Создать задачу для обработчика
        """

        if await self.filter.check(package):
            return await self.callback(self.module, package)
    