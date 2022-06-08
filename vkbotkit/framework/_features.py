"""
Copyright 2022 kensoi
"""
import asyncio
import os
import time
import logging
import logging.config
from importlib.util import (
    spec_from_file_location,
    module_from_spec)
from .. import utils, objects
from ..objects import enums


class Logger:
    """
    docstring patch
    """

    def __init__(
        self, logger_name = None, log_level: objects.enums.LogLevel = objects.enums.LogLevel.INFO,
        file_log = False, print_log = False):
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(log_level.value)
        self.formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        if file_log:
            self.file_handler = logging.FileHandler('.log')
            self.file_handler.setLevel(log_level.value)
            self.file_handler.setFormatter(self.formatter)
            self.logger.addHandler(self.file_handler)

        if print_log:
            self.stream_handler = logging.StreamHandler()
            self.stream_handler.setLevel(log_level.value)
            self.stream_handler.setFormatter(self.formatter)
            self.logger.addHandler(self.stream_handler)


class Assets:
    """
    Toolkit.assets
    """

    def __init__(self, sdk, assets = None):
        if not assets:
            assets = objects.PATH_SEPARATOR.join([os.getcwd(),"assets", ""])

        if assets[-1] != objects.PATH_SEPARATOR:
            assets += objects.PATH_SEPARATOR

        if assets.startswith("."):
            assets = os.getcwd() + assets[1:]

        if not os.path.exists(assets):
            os.mkdir(assets)
            sdk.log(message = "Assets directory was made by framework")

        if not os.path.isdir(assets):
            raise Exception("Assets directory should be a folder")

        self.__path = assets


    def __call__(self, *args, **kwargs):
        args = list(args)
        if len(args) > 0:
            args[0] = self.__path + args[0]

        elif 'file' in kwargs:
            kwargs['file'] = self.__path + kwargs['file']

        return open(*args, **kwargs)


    def __exit__(self, exc_type, exc_value, traceback):
        pass


class Replies:
    """
    docstring patch
    """

    def __init__(self) -> None:
        """
        docstring patch
        """

        self.__wait_list = {}

    def check(self, pkg):
        """
        docstring patch
        """

        for _, task_obj in self.__wait_list.items():
            if task_obj.check(pkg):
                return True


    async def get(self, pkg):
        """
        docstring patch
        """

        task_obj = ReplyTask(pkg)
        task_id = f"${time.time()}_{pkg.peer_id}_{pkg.from_id}"
        self.__wait_list[task_id] = task_obj

        while not task_obj.ready:
            await asyncio.sleep(1)

        self.__wait_list.pop(task_id, None)
        return task_obj.package


class ReplyTask:
    """
    docstring patch
    """

    def __init__(self, pkg):
        self.__chat = pkg.peer_id
        self.__from = pkg.from_id
        self.ready = False
        self.package = None

    def check(self, pkg):
        """
        docstring patch
        """

        if self.__chat == pkg.peer_id and self.__from == pkg.from_id:
            self.ready = True
            self.package = pkg
            return True


class CallbackLib:
    """
    раздел vkbotkit для работы с библиотеками
    """

    def __init__(self, toolkit, libdir):
        """
        docstring patch
        """

        self.__libdir = libdir
        self.handlers = []
        self.toolkit = toolkit


    def import_library(self):
        """
        Импортировать все плагины из каталога library (либо иного другого)
        """

        if not self.__libdir:
            self.__libdir = os.getcwd() + objects.PATH_SEPARATOR + 'library'

        if self.__libdir.startswith("."):
            self.__libdir = os.getcwd() + self.__libdir[1:]

        if not os.path.exists(self.__libdir):
            os.mkdir(self.__libdir)
            self.toolkit.log("libdir created")

        if not os.path.isdir(self.__libdir):
            raise TypeError("libdir should be dir, not a file!")

        listdir = utils.filter_folders(self.__libdir)

        for module_path in listdir:
            spec = spec_from_file_location(
                module_path[len(self.__libdir) + 1:].replace(".py", "", 1), module_path
                )
            module = module_from_spec(spec)
            spec.loader.exec_module(module)
            self.import_module(module.Main)


    def import_module(self, lib = None):
        """
        Импортировать специфический модуль
        """

        self.handlers.extend(lib()._handlers)
        self.handlers.sort(key = lambda h: h.callback_function.priority)


    async def parse(self, toolkit, package):
        """
        Обработать уведомление с помощью библиотек
        """

        if not isinstance(package, objects.data.Package):
            package = await self._convert_event(package)

        if not hasattr(package, "toolkit"):
            package.toolkit = toolkit

        if not toolkit.replies.check(package):
            # проверяем, ожидается ли ответ от адресата данного уведомления
            await asyncio.gather(*map(lambda h: h.create_task(package), self.handlers))


    async def _convert_event(self, event):
        """
        Обработать уведомление по типу
        """
        event_type = event['type'].upper()
        if hasattr(enums.Events, event_type):
            event_type = getattr(enums.Events, event_type)
        else:
            raise Exception("Unsupported event")

        if event_type == enums.Events.MESSAGE_NEW:
            package_raw = event['object']['message']
            package_raw['params'] = event['object']['client_info']
            package_raw['items'] = utils.convert_command(package_raw['text'])
        else:
            package_raw = event['object']

        package_raw['type'] = event_type
        return objects.data.Package(package_raw)
