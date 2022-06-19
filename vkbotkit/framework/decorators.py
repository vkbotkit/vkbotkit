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
        return "<vkbotkit.framework.decorators.Handler>"


    def run(self):
        """
        Запуск обработчика внутри потока
        """

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_forever()

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
            response = await self.callback(self.module, package)
            return response

def callback(callback_filter):
    """
    Прикрепить к обработчику фильтры
    """

    def decorator(function):
        def wrap(self):
            return Handler(callback_filter, function, self)

        return wrap

    return decorator
    