"""
Copyright 2022 kensoi
"""

import six


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
        iterated = six.iteritems(kwargs)
        list_instances = filter(lambda _, value: isinstance(value, (list, tuple)), iterated)
        comma_joined = {key: ','.join(str(x) for x in value) for key, value in list_instances}

        return await self.method(self.string, **comma_joined)


    def __repr__(self):
        return "<vkbotkit.framework.api.GetAPI>"
