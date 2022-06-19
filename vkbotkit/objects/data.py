"""
Copyright 2022 kensoi
"""

class Response:
    """
    Объект результата запроса к серверу ВКонтакте
    """

    def __init__(self, entries):
        self.__dict__.update(entries)

        for i in self.__dict__:
            setattr(self, i, self.__convert(getattr(self, i)))

        self.__raw = entries


    def __convert(self, attr):
        attr_type = type(attr)

        if attr_type == dict:
            return Key(attr)

        elif attr_type == list:
            return [self.__convert(i) for i in attr]

        else:
            return attr

    def __str__(self):
        return str(self.__raw)


    def __dict__(self):
        return self.__raw


    def __repr__(self):
        return '<vkbotkit.objects.data.Response>'


class Key(Response):
    """
    Объект поля в результате
    """

    def __repr__(self):
        """
        docstring patch
        """

        return '<vkbotkit.objects.data.Key>'


class Expression:
    """
    Объект переменной для системы VKBotKit
    """

    __slots__ = ('type', 'value')


    def __init__(self):
        self.type = None
        self.value = None


    def __str__(self):
        return str(self.value)


    def __int__(self):
        return self.value


    def __list__(self):
        return self.value


    def __repr__(self):
        return '<vkbotkit.objects.data.Expression>'


class Package(Response):
    """
    Объект обработанного уведомления
    """

    id = 0
    date = 0
    random_id = 0
    peer_id = 1
    from_id = 1
    items = []
