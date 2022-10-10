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
        map(lambda i: setattr(self, i, self.__convert(getattr(self, i))), self.__dict__)


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

    important: bool
    is_cropped: bool
    was_listened: bool

    admin_author_id: int
    conversation_message_id: int
    date: int
    from_id: int
    id: int
    members_count: int
    peer_id: int
    pinned_at: int
    random_id: int
    update_time: int

    message_tag: str
    payload: str
    text: str
    ref: str
    
    items: list
    attachments: list
    fwd_messages: list

    action: Key
    geo: Key
    keyboard: Key
    reply_message: Key
