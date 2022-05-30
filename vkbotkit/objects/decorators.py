import asyncio

"""
Copyright 2022 kensoi
"""

class handler():
    """
    docstring patch
    """

    def __init__(self, filter, libraryCallback, library_module):
        """
        docstring patch
        """

        self.filter = filter
        self.libraryModule = library_module
        self.libraryCallback = libraryCallback


    def __repr__(self):
        """
        docstring patch
        """

        return f"<vkbotkit.objects.decorators.handler({self.name})>"


    def run(self):
        """
        docstring patch
        """

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_forever()

    @property
    def loop(self):
        """
        docstring patch
        """

        return asyncio.get_event_loop()
    

    async def create_task(self, package):
        """
        docstring patch
        """

        if await self.filter.check(package):
            return await self.libraryCallback(self.libraryModule, package)

def callback(filter):
    """
    docstring patch
    """

    def decorator(callback):
        def wrap(self):
            return handler(filter, callback, self)

        return wrap

    return decorator
    