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


    async def create_task(self, package, toolkit):
        """
        Создать задачу для обработчика
        """

        if await self.filter.check(package):
            return await self.callback(self.module, package, toolkit)


class Library:
    """
    Объект плагина
    """

    def __init__(self):
        methods = set(dir(self)) - set(dir(object()))

        methods_map = map(lambda i: getattr(self, i), methods)
        methods_filtered = filter(callable, methods_map)
        methods_inited = map(lambda i: i(), methods_filtered)
        self.handlers = list(filter(lambda i: isinstance(i, Wrapper), methods_inited))

    def __repr__(self):
        return "<vkbotkit.objects.callback.Library>"


def callback(command_filter):
    """
    Прикрепить к обработчику фильтры
    """
    def decorator(command_handler):
        def wrapper(self):
            return Wrapper(command_filter, command_handler, self)

        return wrapper

    return decorator
