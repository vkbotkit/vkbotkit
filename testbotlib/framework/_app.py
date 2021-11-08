from testbotlib.objects.data import response
from . import _features, _api
from .. import utils, objects
import asyncio
import os
import random
import typing


class sdk:
    def __init__ (self, token, assets_path = None, log_level: objects.enums.log_level = objects.enums.log_level.INFO, file_log = False, print_log = False):
        self.__event_loop = asyncio.get_event_loop()
        self.__print_log = not not print_log
        self.__logger = _features._logger("testbotlib", log_level, file_log, print_log)
        
        self.assets = _features._assets(self, assets_path)
        self.core = _api.core(token)
        self.replies = _features.replies()
        self.uploader = _api.uploader(self)


    @property
    def api(self):
        return self.core._api
        

    async def start_polling(self, library): # only for group bots
        if self.core._longpoll._is_polling:
            self.log("polling already started", log_level=objects.enums.log_level.ERROR)
            raise Exception("polling already started")

        self.core._longpoll._is_polling = True
        group_info = await self.api.groups.getById()

        self.log("poll started")
        await self.core._longpoll._longpoll__update_longpoll_server(group_info[0].id)

        self.log("[%s] polling is started" % group_info[0].screen_name)
        while self.core._longpoll._is_polling:
            for event in await self.core._longpoll._check(group_info[0].id):
                print(event)


    def is_polling(self):
        return self.core._longpoll._is_polling


    def stop_polling(self):
        if self.core._longpoll._is_polling:
            self.core._longpoll._is_polling = False
            self.log("polling finished", objects.enums.log_level.DEBUG)

        else:
            self.log("attempt to stop poll cycle that is not working now", objects.enums.log_level.WARNING)



    def log(self, message, log_level: objects.enums.log_level = objects.enums.log_level.INFO):
        self.__logger.logger.log(level = log_level.value, msg = message)

    
    def gen_random(self):
        return int(random.random() * 999999)

    async def getBotData(self, fields):
        page_info = await self.api.users.get(fields="screen_name, " + ", ".join(fields), raw=True)

        if len(page_info) > 0:
            bot_type = "id"

        else:
            page_info = await self.api.groups.getById(fields = ", ".join(fields), raw=True)

            if len(page_info) > 0:
                bot_type = "club"

        return objects.data.response({
            **page_info, "bot_type": bot_type
        })


    async def getBotMention(self):
        res = await self.getBotData()
        return "[%s%i|%s]" % (res.bot_type, res.id, res.screen_name)


    async def send_reply(self, package: objects.data.package, message: typing.Optional[str]=None, delete_last:bool = False, **kwargs):
        if not 'peer_id' in kwargs: kwargs['peer_id'] = package.peer_id
        kwargs['random_id'] = self.gen_random()
        if message: kwargs['message'] = message

        if delete_last:
            await self.delete_message(package)
            
        return await self.api.messages.send(**kwargs)
    

    async def delete_message(self, package):
        return await self.api.messages.delete(conversation_message_ids = package.conversation_message_id, peer_id = package.peer_id, delete_for_all = 1)



class bot:
    def __init__(self, token, assetpath = None, libpath = None, log_level = None, file_log = False, print_log = False):
        if not assetpath:
            assetpath = os.getcwd() + objects.path_separator + "assets"

        if not libpath:
            libpath = os.getcwd() + objects.path_separator + "library"
        
        self.__library = _features.callbacklib(libpath)
        self.__sdk = sdk(token, assetpath, log_level, not not file_log, not not print_log)


    @property
    def sdk(self):
        return self.__sdk


    @property
    def library(self):
        return self.__library
        
    async def start_polling(self):
        await self.__sdk.start_polling(self.__library)