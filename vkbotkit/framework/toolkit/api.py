"""
Copyright 2023 kensoi
"""


class GetAPI:
    """
    Обёртка вокруг сессии клиента для упрощённого доступа к VK BOT API
    """

    __slots__ = ('https', 'method', 'string')

    def __init__(self, http, method, string = None):
        self.https = http
        self.method = method
        self.string = string


    def __getattr__(self, method):
        self.string = self.string + "." if self.string else ""

        return GetAPI(self.https, self.method,
            (self.string if self.method else '') + method)


    async def __call__(self, **kwargs):
        for key, value in kwargs.items():
            if isinstance(value, (list, tuple)):
                kwargs[key] = ','.join(str(x) for x in value)

        return await self.method(self.string, kwargs)


    def __repr__(self):
        return "<vkbotkit.framework.api>"
