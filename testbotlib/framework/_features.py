import asyncio
from logging import Logger, log
import time
import os
import typing
from importlib.util import (
    spec_from_file_location,
    module_from_spec)

from ..objects.data import response

from .. import utils
from . import _api


class _assets:
    def __init__(self, sdk, assets = None):
        if not assets:
            assets = utils.path_separator.join([os.getcwd(),"assets", ""])

        if assets[-1] != utils.path_separator: assets += utils.path_separator

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


class sdk:
    def __init__ (self, token, group_id, assets_path = None, logger = None):
        self.__group_id = group_id
        self.__event_loop = asyncio.get_event_loop()
        self.__library = []
        self.__logger = logger
        
        self.assets = _assets(self, assets_path)
        self.core = _api.core(token, group_id, logger = logger)
        self.replies = replies()
        self.uploader = _api.uploader(self.core._api, self.assets)

        

    async def start_polling(self, debug:bool=True):
        self.core._longpoll._is_polling = True
        self.debug = debug

        self.log("poll started")
        await self.core._longpoll._longpoll__update_longpoll_server()

        while self.core._longpoll._is_polling:
            for event in await self.core._longpoll._check():
                pass


    def is_polling(self):
        return self.core._longpoll._is_polling


    def stop_polling(self):
        self.core._longpoll._is_polling = False
        self.log("polling finished", "debug")


    def log(self, message, log_level="info"):
        print(f"[{log_level}] message")


    def update_lib(self, lib):
        self.__library = []


class callbacklib:
    def __init__(self, sdk, libdir):
        self.sdk = sdk
        self.__libdir = libdir
        self.handlers = []

    def import_library(self):
        if not self.__libdir:
            self.__libdir = os.getcwd() + utils.path_separator + 'library'

        if self.__libdir.startswith("."):
            self.__libdir = os.getcwd() + self.__libdir[1:]

        if not os.path.exists(self.__libdir):
            os.mkdir(self.__libdir)
            self.sdk.log("library directory was made by framework")

        if not os.path.isdir(self.__libdir):
            raise TypeError("Libdir should be dir, not a file!")

        listdir = filter_folders(self.__libdir)

        for module_path in listdir:
            spec = spec_from_file_location(module_path[len(self.__libdir) + 1:].replace(".py", "", 1), module_path)
            module = module_from_spec(spec)
            spec.loader.exec_module(module)
            self.import_module(module.Main)

    def import_module(self, library = None):
        self.handlers.extend(library()._handlers)
        self.handlers.sort(key = lambda h: h.filter.priority)

def convert_path(path: typing.Optional[str] = None, path_type: str = ""):
    path_c = os.getcwd()
    if path:
        if path[0] == '.':
            path_c += path[True:]
        else:
            path_c = path

    return utils.path_separator.join([path_c, path_type])


def filter_folders(libdir):
    files_list = os.listdir(libdir)
    response = []

    for name in files_list:
        obj_path = utils.path_separator.join([libdir, name])
        if os.path.isfile(obj_path):
            if name.endswith(".py"):
                response.append(obj_path)

        elif "__init__.py" in os.listdir(obj_path):
            response.append(utils.path_separator.join([obj_path, "__init__.py"]))
    
    return response