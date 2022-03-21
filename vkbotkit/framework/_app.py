from vkbotkit.objects.data import response
from . import _features, _api
from .. import objects
import asyncio
import os
import random
import typing


class toolkit:
    def __init__ (self, token, assets_path = None):
        self.__logger = None
        self.assets = _features._assets(self, assets_path)
        self.core = _api.core(token)
        self.replies = _features.replies()
        self.uploader = _api.uploader(self)

    @property
    def __event_loop(self):
        return asyncio.get_event_loop()


    @property
    def api(self) -> _api.api:
        return self.core._api
        

    async def start_polling(self, library:typing.Optional[_features.callbacklib] = None) -> None: # only for group bots
        if not library:
            raise Exception("You should connect a library here")

        if self.core._longpoll._is_polling:
            self.log("polling already started", log_level=objects.enums.log_level.ERROR)
            raise Exception("polling already started")

        self.core._longpoll._is_polling = True
        group_info = await self.api.groups.getById()
        await self.core._longpoll._longpoll__update_longpoll_server(group_info[0].id)
        
        self.log("[%s] polling is started" % group_info[0].screen_name)

        while self.core._longpoll._is_polling:
            for event in await self.core._longpoll._check(group_info[0].id):
                self.__event_loop.create_task(library.parse(self, event))

    def is_polling(self) -> bool:
        return self.core._longpoll._is_polling


    def stop_polling(self) -> None:
        if self.core._longpoll._is_polling:
            self.core._longpoll._is_polling = False
            self.log("polling finished", objects.enums.log_level.DEBUG)

        else:
            self.log("attempt to stop poll cycle that is not working now", objects.enums.log_level.WARNING)


    def configure_logger(self, log_level: objects.enums.log_level = objects.enums.log_level.INFO, file_log = False, print_log = False):
        self.__logger = _features._logger("vkbotkit", log_level, file_log, print_log)


    def log(self, message, log_level: objects.enums.log_level = objects.enums.log_level.INFO) -> None:
        if self.__logger:
            self.__logger.logger.log(level = log_level.value, msg = message)

    
    def gen_random(self) -> int:
        return int(random.random() * 999999)


    def create_keyboard(self, one_time:bool=False, inline:bool=False) -> objects.keyboard.keyboard:
        return objects.keyboard.keyboard(one_time, inline)



    async def get_me(self, fields=None) -> objects.data.response:
        if not fields:
            fields = ['screen_name']

        page_info = await self.api.users.get(fields=', '.join(fields), raw=True)
        if len(page_info) > 0:
            bot_type = "id"

        else:
            page_info = await self.api.groups.getById(fields = ", ".join(fields), raw=True)

            if len(page_info) > 0:
                bot_type = "club"
        
        return objects.data.response({
            **page_info[0], "bot_type": bot_type
        })


    async def get_my_mention(self) -> str:
        res = await self.get_me()

        return "[%s%i|%s]" % (res.bot_type, res.id, res.screen_name)


    async def send_reply(self, package: objects.data.package, message: typing.Optional[str]=None, delete_last:bool = False, **kwargs):
        if not 'peer_id' in kwargs: 
            kwargs['peer_id'] = package.peer_id

        if not 'random_id' in kwargs:
            kwargs['random_id'] = self.gen_random()

        if not 'message' in kwargs and message: 
            kwargs['message'] = message

        if delete_last:
            await self.delete_message(package)
            
        return await self.api.messages.send(**kwargs)
    

    async def delete_message(self, package):
        return await self.api.messages.delete(conversation_message_ids = package.conversation_message_id, peer_id = package.peer_id, delete_for_all = 1)



class librabot:
    def __init__(self, token, assetpath = None, libpath = None):
        if not assetpath:
            assetpath = os.getcwd() + objects.path_separator + "assets"

        if not libpath:
            libpath = os.getcwd() + objects.path_separator + "library"
        
        self.library = _features.callbacklib(libpath)
        self.toolkit = toolkit(token, assetpath)


    async def start_polling(self) -> None:
        await self.toolkit.start_polling(self.library)