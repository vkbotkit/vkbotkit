"""
Copyright 2022 kensoi
"""

import asyncio
import os
from importlib.util import spec_from_file_location, module_from_spec

from .toolkit.toolkit import ToolKit
from ..utils import map_folders, toolkit_raise
from ..objects import exceptions, Library, PATH_SEPARATOR
from ..objects.enums import LogLevel
from ..objects.package import Package


class LibraryParser:
    """
    Обработчик библиотек, содержащихся в ./library
    """

    def __init__(self) -> None:
        self.handlers = []
        self.__libdir = None


    def __repr__(self) -> str:
        return "<vkbotkit.framework.library>"


    def import_library(self, toolkit: ToolKit, library_path: str) -> None:
        """
        Импортировать все плагины из каталога library (либо иного другого)
        """

        self.__libdir = library_path

        if self.__libdir.startswith("."):
            self.__libdir = os.getcwd() + self.__libdir[1:]

        if not os.path.exists(self.__libdir):
            message = "library doesn't exist"
            exception = exceptions.LibraryExistionError

            toolkit_raise(toolkit, message, LogLevel.DEBUG, exception)

        if not os.path.isdir(self.__libdir):
            message = "plugin library folder should be a directory, not a file"
            exception = exceptions.LibraryTypeError

            toolkit_raise(toolkit, message, LogLevel.DEBUG, exception)

        for module_path in map_folders(self.__libdir):
            module_root = module_path[len(self.__libdir) + 1:]
            module_name = module_root.replace(PATH_SEPARATOR + "__init__.py", "")
            module_path_name = module_path[module_path.rfind(PATH_SEPARATOR)+1:]
            module_path_name = module_path_name.replace(".py", "", 1)

            spec = spec_from_file_location(module_path_name,module_path)
            loaded_module = module_from_spec(spec)
            spec.loader.exec_module(loaded_module)
            self.import_module(loaded_module.Main())

            toolkit.log(f"Importing plugin {module_name} succeed", LogLevel.DEBUG)

        self.handlers.sort(key = lambda h: h.filter.priority)


    def import_module(self, main_lib: Library) -> None:
        """
        Импортировать специфический модуль (должен быть унаследован от
        Library и при передаче в функцию проинициализирован)
        """

        if isinstance(main_lib, Library):
            self.handlers.extend(main_lib.get_handlers())


    async def parse(self, toolkit: ToolKit, package: Package) -> None:
        """
        Обработать уведомление с помощью библиотек
        """

        if not isinstance(package, Package):
            message = "plugin library folder should be a directory, not a file"
            exception = exceptions.LibraryTypeError

            toolkit_raise(toolkit, message, LogLevel.DEBUG, exception)

        if not toolkit.messages.check_for_waiting_reply(package):
            handler_tasks = map(lambda h: h.create_task(toolkit, package), self.handlers)
            await asyncio.gather(*handler_tasks)
