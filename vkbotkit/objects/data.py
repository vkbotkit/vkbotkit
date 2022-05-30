import typing

"""
Copyright 2022 kensoi
"""

class expression:
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

        return self.value


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

        return '<vkbotkit.objects.data.expression(:::{}:{}:::)>'.format(self.value, self.value)


def task(package):
    """
    Объект задачи для системы ожидания ответов
    """

    return "$" + str(package.peer_id)+ "_" + str(package.from_id)


class mention:
    """
    docstring patch
    """

    __slots__ = ('id', 'call') 


    def __init__(self, text):
        """
        docstring patch
        """

        if text[0] != "[" or text[-1] != "]":
            raise Exception(f"can't init mention from this text: \"{text}\" ")

        text = text[1:-1]
        OBJ, self.call = text.split("|")

        if OBJ.startswith('id'):
            self.id = int(OBJ[2:])

        elif OBJ.startswith('club'):
            self.id = -int(OBJ[4:])

        else:
            self.id = -int(OBJ[6:])


    def __int__(self):
        """
        docstring patch
        """

        return self.id 


    def __str__(self):
        """
        docstring patch
        """

        return self.call


    def __repr__(self):
        """
        docstring patch
        """

        if self.id > 0:
            return f"[id{self.id}|{self.call}]"
        else:
            return f"[club{-self.id}|{self.call}]"


class response:
    """
    docstring patch
    """

    def __init__(self, entries):
        """
        docstring patch
        """

        self.__dict__.update(entries)

        for i in self.__dict__.keys():
            setattr(self, i, self.__convert(getattr(self, i)))

        self.raw = entries
            

    def __convert(self, attr):
        """
        docstring patch
        """

        attr_type = type(attr)

        if attr_type == dict:
            return key(attr)

        elif attr_type == list:
            return [self.__convert(i) for i in attr]
        
        else:
            return attr  


    def __repr__(self):
        """
        docstring patch
        """

        return '<{}({})>'.format(type(self), self.raw)
  


class key(response):
    """
    docstring patch
    """

    pass


class package(response):
    """
    Объект обработанного уведомления
    """

    __item = "$item"
    __items = "$items"
    __mention = "$mention"
    __mentions = "$mentions"
    __expr = "$expr"
    __exprs = "$exprs"

    id = 0
    date = 0
    random_id = 0
    peer_id = 1
    from_id = 1
    items = []
