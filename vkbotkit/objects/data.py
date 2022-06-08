"""
Copyright 2022 kensoi
"""

class Response:
    """
    docstring patch
    """

    def __init__(self, entries):
        """
        docstring patch
        """

        self.__dict__.update(entries)

        for i in self.__dict__:
            setattr(self, i, self.__convert(getattr(self, i)))

        self.raw = entries


    def __convert(self, attr):
        """
        docstring patch
        """

        attr_type = type(attr)

        if attr_type == dict:
            return Key(attr)

        elif attr_type == list:
            return [self.__convert(i) for i in attr]

        else:
            return attr


    def __repr__(self):
        """
        docstring patch
        """

        return f'<{type(self)}({self.raw})>'


class Key(Response):
    """
    docstring patch
    """


class Expression:
    """
    docstring patch
    """

    __slots__ = ('type', 'value')


    def __init__(self):
        """
        docstring patch
        """

        self.type = None
        self.value = None


    def __str__(self):
        """
        docstring patch
        """

        return str(self.value)


    def __int__(self):
        """
        docstring patch
        """

        return self.value


    def __list__(self):
        """
        docstring patch
        """

        return self.value


    def __repr__(self):
        """
        docstring patch
        """

        return f'<vkbotkit.objects.data.Expression(:::{self.value}:{self.value}:::)>'


class Package(Response):
    """
    Объект обработанного уведомления
    """

    # __item = "$item"
    # __items = "$items"
    # __mention = "$mention"
    # __mentions = "$mentions"
    # __expr = "$expr"
    # __exprs = "$exprs"

    id = 0
    date = 0
    random_id = 0
    peer_id = 1
    from_id = 1
    items = []

def task(message: Package):
    """
    Объект задачи для системы ожидания ответов
    """

    return "$" + str(message.peer_id)+ "_" + str(message.from_id)


class Mention:
    """
    docstring patch
    """

    __slots__ = ('value', 'key', 'repr')


    def __init__(self, page_id = None, page_key = None):
        """
        docstring patch
        """
        self.value = page_id
        if page_id > 0:
            self.key = page_key if page_key else f"@id{page_id}"
            self.repr = f"[id{page_id}|{self.key}]"
        else:
            self.key = page_key if page_key else f"@public{abs(page_id)}"
            self.repr = f"[public{abs(page_id)}|{self.key}]"


    def __int__(self):
        """
        docstring patch
        """

        return self.value


    def __str__(self):
        """
        docstring patch
        """

        return self.key


    def __repr__(self):
        return self.repr

def dump_mention(text):
    """
    Конвертировать текст формата [id1|text] в объект Mention
    """
    if text[0] != "[" or text[-1] != "]":
        raise Exception(f"can't init mention from this text: \"{text}\" ")

    text = text[1:-1]
    obj, key = text.split("|")

    if obj.startswith('id'):
        value = int(obj[2:])
        return Mention(value, key)

    elif obj.startswith('club'):
        value = int(obj[4:])
        return Mention(value, key)

    elif obj.startswith('public'):
        value = int(obj[6:])
        return Mention(value, key)
        
    raise TypeError("Invalid page id (should be club, public or id)")