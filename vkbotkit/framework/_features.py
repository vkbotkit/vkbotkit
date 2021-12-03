import asyncio
import os
import time
import typing
import logging
import logging.config
from importlib.util import (
    spec_from_file_location,
    module_from_spec)

from vkbotkit.objects import enums

from .. import utils, objects


class _logger:
    def __init__(self, logger_name = None, log_level: objects.enums.log_level = objects.enums.log_level.INFO, file_log = False, print_log = False):
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(log_level.value)
        self.formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        if file_log:
            self.fh = logging.FileHandler('.log')
            self.fh.setLevel(log_level.value)
            self.fh.setFormatter(self.formatter)
            self.logger.addHandler(self.fh)

        if print_log:
            self.ch = logging.StreamHandler()
            self.ch.setLevel(log_level.value)
            self.ch.setFormatter(self.formatter)
            self.logger.addHandler(self.ch)

        # 'application' code


class _assets:
    def __init__(self, sdk, assets = None):
        if not assets:
            assets = objects.path_separator.join([os.getcwd(),"assets", ""])

        if assets[-1] != objects.path_separator: assets += objects.path_separator

        if assets.startswith("."):
            assets = os.getcwd() + assets[1:]

        if not os.path.exists(assets):
            os.mkdir(assets)
            sdk.log(message = "Assets directory was made by framework")

        if not os.path.isdir(assets):
            raise ("Assets directory should be a folder")
        
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


class replies:
    def __init__(self) -> None:
        self.__wait_list = {}

    def check(self, pkg, from_poll = False):
        for task_id, task_obj in self.__wait_list.items():
            if task_obj.check(pkg): return True 
            

    async def get(self, pkg):
        task_obj = reply_task(pkg)
        task_id = f"${time.time()}_{pkg.peer_id}_{pkg.from_id}"
        self.__wait_list[task_id] = task_obj

        while not task_obj.ready:
            await asyncio.sleep(1)
            
        self.__wait_list.pop(task_id, None)
        return task_obj.pkg


class reply_task:
    def __init__(self, pkg):
        self.__chat = pkg.peer_id
        self.__from = pkg.from_id
        self.ready = False
        
    def check(self, pkg):
        if self.__chat == pkg.peer_id and self.__from == pkg.from_id:
            self.ready = True
            self.pkg = pkg
            return True


class callbacklib:
    def __init__(self, libdir):
        self.__libdir = libdir
        self.handlers = []


    def import_library(self):
        if not self.__libdir:
            self.__libdir = os.getcwd() + objects.path_separator + 'library'

        if self.__libdir.startswith("."):
            self.__libdir = os.getcwd() + self.__libdir[1:]

        if not os.path.exists(self.__libdir):
            os.mkdir(self.__libdir)
            self.sdk.log("libdir created")

        if not os.path.isdir(self.__libdir):
            raise TypeError("libdir should be dir, not a file!")

        listdir = utils.filter_folders(self.__libdir)

        for module_path in listdir:
            spec = spec_from_file_location(module_path[len(self.__libdir) + 1:].replace(".py", "", 1), module_path)
            module = module_from_spec(spec)
            spec.loader.exec_module(module)
            self.import_module(module.Main)


    def import_module(self, lib = None):
        self.handlers.extend(lib()._handlers)
        self.handlers.sort(key = lambda h: h.filter.priority)


    async def parse(self, toolkit, package):
        if not isinstance(package, objects.data.package):
            package = await self._convert_event(package)

        if not hasattr(package, "toolkit"):
            package.toolkit = toolkit

        if not toolkit.replies.check(package):
            results = await asyncio.gather(*map(lambda h: h.create_task(package), self.handlers))


    async def _convert_event(self, event):
        if hasattr(enums.events, event['type']):
            event_type = getattr(enums.events, event['type'])
        else: 
            raise Exception("Unsupported event")

        if event_type == enums.events.message_new:
            package_raw = event['object']['message']
            package_raw['params'] = event['object']['client_info']
            package_raw['items'] = utils.convert_command(package_raw['text'])
        else:
            package_raw = event['object']

        package_raw['type'] = event_type
        
        return objects.data.package(package_raw)