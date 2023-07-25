"""
Copyright 2023 kensoi
"""


def convert_to_key(attr):
    if isinstance(attr, dict):
        return Key(attr)

    if isinstance(attr, list):
        return list(map(convert_to_key, attr))

    return attr


class Response:
    """
    Объект результата запроса к серверу ВКонтакте
    """

    raw: dict

    def __init__(self, entries):
        for key, value in entries.items():
            self.__dict__[key] = convert_to_key(value)

        self.raw = entries


    def __str__(self):
        return f'<vkbotkit.objects.data.Response {self.raw}>'


    def __repr__(self):
        return f'<vkbotkit.objects.data.Response {self.raw}>'


class Key(Response):
    """
    Объект поля в результате
    """


    def __repr__(self):
        return f'<vkbotkit.objects.data.Key {self.raw}>'


    def __str__(self):
        return f'<vkbotkit.objects.data.Key {self.raw}>'
