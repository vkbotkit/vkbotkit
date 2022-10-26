"""
Copyright 2022 kensoi
"""

class Response:
    """
    Объект результата запроса к серверу ВКонтакте
    """

    raw: dict

    def __init__(self, entries):
        self.__dict__.update(entries)
        self.raw = entries

        for i in self.__dict__:
            setattr(self, i, self.__convert(getattr(self, i)))


    def __convert(self, attr):
        attr_type = type(attr)

        if attr_type == dict:
            return Key(attr)

        if attr_type == list:
            return list(map(self.__convert, attr))

        return attr


    def __str__(self):
        return str(self.raw)


    def __repr__(self):
        return '<vkbotkit.objects.data.Response>'


class Key(Response):
    """
    Объект поля в результате
    """

    def __repr__(self):
        return '<vkbotkit.objects.data.Key>'
