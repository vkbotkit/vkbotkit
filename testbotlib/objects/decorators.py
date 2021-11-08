import typing
from . import exceptions

from .enums import events as enums_events
from .enums import action as enums_action
import asyncio
import threading
import typing

class handler(threading.Thread):
    def __init__(self, filter, libraryCallback, library_module = None):
        threading.Thread.__init__(self)
        self.daemon = True
        self.filter = filter
        self.library_module = library_module
        self.libraryCallback = libraryCallback

        self.start()


    def __repr__(self):
        return f"<libragram.objects.decorators.handler({self.name})>"


    def run(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()


    async def __create_task(self, tools, package):
        parse_args = []

        if self.library_module: 
            parse_args.append(self.library_module)

        parse_args.append(package)
        self.loop.create_task(self.libraryCallback(*parse_args))
    

    async def create_task(self, tools, package):
        if await self.filter.check(package):
            asyncio.run_coroutine_threadsafe(self.__create_task(tools, package), self.loop)


def callback(filter, bot = None):
    def decorator(callback):
        # if bot:
        #     bot.upload_handler(handler(filter, callback))
        #     return

        # else:
        def wrap(self):
            return handler(filter, callback, self)

        return wrap

    return decorator