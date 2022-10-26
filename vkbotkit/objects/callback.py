"""
Copyright 2022 kensoi
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


class Library:
    """
    Объект плагина
    """

    def __repr__(self):
        return "<vkbotkit.objects.callback.Library>"


    def get_handlers(self):
        """
        Получить список обработчиков
        """

        attr_name_set = set(dir(self)) - set(dir(Library()))
        attr_map = map(lambda i: getattr(self, i), attr_name_set)
        attr_inited = map(lambda i: i(), filter(callable, attr_map))
        return list(filter(lambda i: isinstance(i, Wrapper), attr_inited))


def callback(command_filter):
    """
    Прикрепить к обработчику фильтры
    """

    def decorator(command_handler):
        def wrapper(self):
            return Wrapper(command_filter, command_handler, self)

        return wrapper

    return decorator
