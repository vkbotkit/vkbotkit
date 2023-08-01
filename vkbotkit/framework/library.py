"""
Copyright 2023 kensoi
"""

import asyncio
import os
import importlib
from watchdog.events import (
    EVENT_TYPE_MODIFIED,
    # EVENT_TYPE_MOVED, EVENT_TYPE_DELETED, EVENT_TYPE_CREATED, EVENT_TYPE_CLOSED, EVENT_TYPE_OPENED
)

from .toolkit.toolkit import ToolKit
from ..utils import (
    parse_path_for_plugins,
    parse_plugin_for_libs,
    toolkit_raise,
    get_library_handlers
)
from ..objects import exceptions, Library
from ..objects.enums import LogLevel
from ..objects.package import Package
from .modify_watcher import ModifyWatcher

class PluginManager:
    """
    Обработчик библиотек, содержащихся в ./library
    """

    def __init__(self, toolkit: ToolKit) -> None:
        self.handlers = []
        self.modules = {}
        self.toolkit = toolkit
        self.__modify_watcher = ModifyWatcher(self.watcher_action)

    def __repr__(self) -> str:
        return "<vkbotkit.framework.library>"


    def import_library(self, folder_name:str) -> None:
        """
        Импортировать все плагины из каталога library (либо иного другого)

        #### Args
            folder_name [str] - название папки с плагинами
        """

        folder_path = os.path.join(os.getcwd(), folder_name)
        self.__modify_watcher.plugin_folders_list.append(folder_name)

        if not os.path.exists(folder_path):
            message = "library doesn't exist"
            exception = exceptions.LibraryExistionError

            toolkit_raise(self.toolkit, message, LogLevel.DEBUG, exception)

        if not os.path.isdir(folder_path):
            message = "plugin library folder should be a directory, not a file"
            exception = exceptions.LibraryTypeError

            toolkit_raise(self.toolkit, message, LogLevel.DEBUG, exception)

        for module_name in parse_path_for_plugins(folder_path):
            module_import_path = f"{folder_name}.{module_name}"
            module = importlib.import_module(module_import_path)

            plugin_lib_count = 0
            self.modules[module_import_path] = []

            for library in parse_plugin_for_libs(module):
                self.init_library(library, module_import_path)
                plugin_lib_count += 1

            self.__modify_watcher.add_watch(module, module_import_path)

            self.toolkit.log(
                f"{module_name}: import of {plugin_lib_count} libs succeed",
                LogLevel.DEBUG
            )

        self.update_handlers()

    def init_library(self, library_constructor:Library, library_module_id: str) -> None:
        """
        Импортировать специфический модуль (должен быть унаследован от
        Library и при передаче в функцию проинициализирован)
        """

        library = library_constructor()

        if not isinstance(library, Library):
            raise TypeError("Library should be Library :)")

        self.modules[library_module_id].append(library)

    def watcher_action(self, action, item):
        """
        function for watchdog
        """

        if action == EVENT_TYPE_MODIFIED:
            plugin = item["plugin"]
            plugin_codename = item["plugin_codename"]
            importlib.reload(plugin)

            plugin_lib_count = 0
            self.modules[plugin_codename] = []

            for library in parse_plugin_for_libs(plugin):
                self.init_library(library, plugin_codename)
                plugin_lib_count += 1

            self.update_handlers()

            self.toolkit.log(
                f"{plugin_codename}: {plugin_lib_count} libs reloaded [{action}]",
                LogLevel.DEBUG
            )

    def update_handlers(self):
        """
        update handlers from library
        """

        self.handlers = []

        for library_list in self.modules.values():
            for library in library_list:
                library_handler_list = get_library_handlers(library)
                self.handlers.extend(library_handler_list)

        self.handlers.sort(key = lambda h: h.filter.priority)

    async def handle(self, package: Package) -> None:
        """
        Обработать уведомление с помощью библиотек
        """

        if not isinstance(package, Package):
            message = "package should be <vkbotkit.objects.package.Package>"
            exception = TypeError

            toolkit_raise(self.toolkit, message, LogLevel.DEBUG, exception)

        if not self.toolkit.messages.check_for_waiting_reply(package):
            loop = asyncio.get_event_loop()
            loop.create_task(self.plugins_task(package))

    async def plugins_task(self, package: Package):
        """
        handling package
        """
        handlers = map(lambda h: h.create_task(self.toolkit, package), self.handlers)
        await asyncio.gather(*handlers)
