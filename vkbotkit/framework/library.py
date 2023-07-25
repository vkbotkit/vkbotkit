"""
Copyright 2022 kensoi
"""

import asyncio
import os
import importlib

from .toolkit.toolkit import ToolKit
from ..utils import (
    parse_path_for_plugins, 
    parse_plugin_for_libs, 
    toolkit_raise, 
    get_library_handlers
)
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


    def import_library(self, toolkit: ToolKit) -> None:
        """
        Импортировать все плагины из каталога library (либо иного другого)
        """

        self.__library_dir = os.getcwd() + PATH_SEPARATOR + "library"
        self.__modify_watcher.paths.append(self.__library_dir)
        self.toolkit = toolkit

        if not os.path.exists(self.__library_dir):
            message = "library doesn't exist"
            exception = exceptions.LibraryExistionError

            toolkit_raise(toolkit, message, LogLevel.DEBUG, exception)

        if not os.path.isdir(self.__library_dir):
            message = "plugin library folder should be a directory, not a file"
            exception = exceptions.LibraryTypeError

            toolkit_raise(toolkit, message, LogLevel.DEBUG, exception)

        for module_name in parse_path_for_plugins(self.__library_dir):
            module_import_path = "library.{}".format(module_name)
            module = importlib.import_module(module_import_path)

            plugin_lib_count = 0

            for library in parse_plugin_for_libs(module):
                self.init_library(library, module_import_path)
                plugin_lib_count += 1
            
            self.__modify_watcher.add_watch(module, module_import_path)

            toolkit.log("{plugin_name}: import of {plugin_lib_count} libs succeed".format(
                plugin_name=module_name,
                plugin_lib_count=plugin_lib_count
            ), LogLevel.DEBUG)


    def init_library(self, library_constructor:Library, library_name: str) -> None:
        """
        Импортировать специфический модуль (должен быть унаследован от
        Library и при передаче в функцию проинициализирован)
        """
        library = library_constructor()

        if not isinstance(library, Library):
            raise TypeError("Library should be Library :)")
        
        self.modules[library_name] = library

    def watcher_action(self, action, item):
        module_path = item['module_path']
        
        self.toolkit.log(f"action: {action}, path: {module_path}", log_level=LogLevel.DEBUG)

        if action == EVENT_TYPE_MODIFIED:
            module = item["module"]
            module_name = item["module_path_name"]
            importlib.reload(module)

            plugin_lib_count = 0

            for library in parse_plugin_for_libs(module):
                self.init_library(library, module_name)
                plugin_lib_count += 1

            self.update_handlers()

            self.toolkit.log("{plugin_name}: {plugin_lib_count} libs reloaded".format(
                plugin_name=module_name,
                plugin_lib_count=plugin_lib_count
            ), LogLevel.DEBUG)

    def update_handlers(self):
        self.handlers = []

        for library in self.modules.values():
            library_handler_list = get_library_handlers(library)
            self.handlers.extend(library_handler_list)

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
