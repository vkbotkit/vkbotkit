import typing
from . import exceptions

from .enums import events as enums_events
from .enums import action as enums_action
import asyncio
import threading
import typing

class handler():
    def __init__(self, filter, libraryCallback, library_module):
        self.filter = filter
        self.libraryModule = library_module
        self.libraryCallback = libraryCallback


    def __repr__(self):
        return f"<libragram.objects.decorators.handler({self.name})>"


    def run(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()
    

    async def create_task(self, package):
        if await self.filter.check(package):
            return await self.libraryCallback(self.libraryModule, package)

def callback(filter):
    def decorator(callback):
        def wrap(self):
            return handler(filter, callback, self)

        return wrap

    return decorator