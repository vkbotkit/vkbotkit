"""
Copyright 2022 kensoi
"""

import asyncio
import os
from importlib.util import spec_from_file_location, module_from_spec

from ..utils import map_folders, convert_command, PATH_SEPARATOR
from ..objects import data, enums, exceptions, LibraryModule


class CallbackLib:
    """
    Рабочий класс vkbotkit для работы с библиотеками
    """

    def __init__(self, libdir):
        self.__libdir = libdir
        self.handlers = []


    def __repr__(self) -> str:
        return "<vkbotkit.features.CallbackLib>"


    def import_library(self, toolkit):
        """
        Импортировать все плагины из каталога library (либо иного другого)
        """

        if self.__libdir.startswith("."):
            self.__libdir = os.getcwd() + self.__libdir[1:]

        if not os.path.exists(self.__libdir):
            os.mkdir(self.__libdir)

            toolkit.log("library doesn't exist",
                log_level = enums.LogLevel.DEBUG)

            raise exceptions.LibraryExistionError("library doesn't exist")

        if not os.path.isdir(self.__libdir):
            toolkit.log("plugin library folder should be a directory, not a file",
                log_level = enums.LogLevel.DEBUG)

            raise exceptions.LibraryTypeError(
                "plugin library folder should be a directory, not a file")

        for module_path in map_folders(self.__libdir):
            module_root = module_path[len(self.__libdir) + 1:]
            module_name = module_root.replace(PATH_SEPARATOR + "__init__.py", "")

            spec = spec_from_file_location(
                module_path[module_path.rfind(PATH_SEPARATOR)+1:].replace(".py", "", 1),
                module_path)
            loaded_module = module_from_spec(spec)
            spec.loader.exec_module(loaded_module)
            self.import_module(loaded_module.Main)

            toolkit.log(f"Importing plugin {module_name} succeed", enums.LogLevel.DEBUG)

        self.handlers.sort(key = lambda h: h.filter.priority)


    def import_module(self, lib):
        """
        Импортировать специфический модуль
        """

        lib_called = lib()

        if isinstance(lib_called, LibraryModule):
            self.handlers.extend(lib_called.handlers)


    async def parse(self, toolkit, package):
        """
        Обработать уведомление с помощью библиотек
        """

        if not isinstance(package, data.Package):
            package = await self._convert_event(package)

        if not hasattr(package, "toolkit"):
            package.toolkit = toolkit

        if not toolkit.replies.check(package):
            await asyncio.gather(*map(lambda h: h.create_task(package), self.handlers))


    async def _convert_event(self, event):
        """
        Обработать уведомление по типу
        """

        event_type_name = event['type'].upper()

        if not hasattr(enums.Events, event_type_name):
            raise Exception("Unsupported event")

        event_type = getattr(enums.Events, event_type_name)

        if event_type == enums.Events.MESSAGE_NEW:
            package_raw = event['object']['message']
            package_raw['params'] = event['object']['client_info']
            package_raw['items'] = convert_command(package_raw['text'])

        else:
            package_raw = event['object']

        package_raw['type'] = event_type

        return data.Package(package_raw)
