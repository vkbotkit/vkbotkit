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
from .modify_watcher import ModifyWatcher

from watchdog.events import (
    EVENT_TYPE_MODIFIED,
    # EVENT_TYPE_MOVED, EVENT_TYPE_DELETED, EVENT_TYPE_CREATED, EVENT_TYPE_CLOSED, EVENT_TYPE_OPENED
)

class LibraryParser:
    """
    Обработчик библиотек, содержащихся в ./library
    """

    def __init__(self) -> None:
        self.handlers = []
        self.modules = {}
        self.__libdir = None
        self.__modify_watcher = ModifyWatcher([self.__libdir], self.watcher_action)


    def __repr__(self) -> str:
        return "<vkbotkit.framework.library>"


    def import_library(self, toolkit: ToolKit, library_path: str) -> None:
        """
        Импортировать все плагины из каталога library (либо иного другого)
        """

        self.__libdir = library_path
        self.__modify_watcher.paths.append(self.__libdir)
        self.toolkit = toolkit

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

            spec = spec_from_file_location(module_path_name, module_path)
            loaded_module = module_from_spec(spec)
            spec.loader.exec_module(loaded_module)
            self.__modify_watcher.add_watch(loaded_module, module_path_name)
            self.import_module(loaded_module)

            toolkit.log(f"Importing plugin {module_name} succeed", LogLevel.DEBUG)


    def import_module(self, loaded_module) -> None:
        """
        Импортировать специфический модуль (должен быть унаследован от
        Library и при передаче в функцию проинициализирован)
        """
        main_lib:Library = loaded_module.Main()

        if isinstance(main_lib, Library):
            self.modules[loaded_module.__name__] = main_lib

    def watcher_action(self, action, item):
        module_path_name = item['module_path_name']
        module_path = item['module_path']
        
        self.toolkit.log(f"action: {action}, path: {module_path}", log_level=LogLevel.DEBUG)

        if action == EVENT_TYPE_MODIFIED:
            spec = spec_from_file_location(module_path_name, module_path)
            loaded_module = module_from_spec(spec)
            spec.loader.exec_module(loaded_module)

            self.import_module(loaded_module)
            self.update_handlers()

    def update_handlers(self):
        self.handlers = []

        for library in self.modules.values():
            self.handlers.extend(library.get_handlers())

        self.handlers.sort(key = lambda h: h.filter.priority)


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
