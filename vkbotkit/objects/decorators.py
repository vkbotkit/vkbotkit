"""
Copyright 2022 kensoi
"""

import asyncio

class Handler():
    """
    docstring patch
    """

    def __init__(self, callback_function, library_callback, library_module):
        """
        docstring patch
        """

        self.callback_function = callback_function
        self.library_module = library_module
        self.library_callback = library_callback


    def __repr__(self):
        """
        docstring patch
        """

        return "<vkbotkit.objects.decorators.Handler>"


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

        if await self.callback_function.check(package):
            return await self.library_callback(self.library_module, package)

def callback(callback_filter):
    """
    docstring patch
    """

    def decorator(function):
        def wrap(self):
            return Handler(callback_filter, function, self)

        return wrap

    return decorator
    