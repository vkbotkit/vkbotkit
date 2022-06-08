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

    __slots__ = ('value', 'key')


    def __init__(self, text):
        """
        docstring patch
        """

        if text[0] != "[" or text[-1] != "]":
            raise Exception(f"can't init mention from this text: \"{text}\" ")

        text = text[1:-1]
        obj, self.key = text.split("|")

        if obj.startswith('id'):
            self.value = int(obj[2:])

        elif obj.startswith('club'):
            self.value = -int(obj[4:])

        else:
            self.value = -int(obj[6:])


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
        """
        docstring patch
        """

        if self.value > 0:
            return f"[id{self.value}|{self.key}]"

        else:
            return f"[club{-self.value}|{self.key}]"
