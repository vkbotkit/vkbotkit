"""
Copyright 2023 kensoi
"""

class Wrapper():
    """
    Класс обработчика события
    """

    def __init__(self, lib_filter, lib_callback, module):
        self.filter = lib_filter
        self.callback = lib_callback
        self.module = module


    def __repr__(self):
        return "<vkbotkit.objects.callback.Wrapper>"


    async def create_task(self, toolkit, package):
        """
        Создать задачу для обработчика
        """
        if await self.filter.check(toolkit, package):
            return await self.callback(self.module, toolkit, package)