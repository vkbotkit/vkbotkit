import typing

class expression:
    __slots__ = ('type', 'value')


    def __init__(self):
        self.type = None
        self.value = None


    def __str__(self):
        return self.value


    def __int__(self):
        return self.value
    

    def __list__(self):
        return self.value


    def __repr__(self):
        return '<{}(:::{}:{}:::)>'.format(repr(type(self))[1:-1], self.value, self.value)


def task(package):
    return "$" + str(package.peer_id)+ "_" + str(package.from_id)


class mention:
    __slots__ = ('id', 'call') 


    def __init__(self, page_id, mention = ""):
        self.id = page_id
        self.call = mention


    def __int__(self):
        return self.id 


    def __str__(self):
        return self.call


    def __repr__(self):
        if self.id > 0:
            return f"[id{self.id}|{self.call}]"
        else:
            return f"[club{-self.id}|{self.call}]"


class response:
    def __init__(self, entries):
        self.__dict__.update(entries)

        for i in self.__dict__.keys():
            setattr(self, i, self.__convert(getattr(self, i)))

        self.raw = entries
            

    def __convert(self, attr):
        attr_type = type(attr)

        if attr_type == dict:
            return key(attr)

        elif attr_type == list:
            return [self.__convert(i) for i in attr]
        
        else:
            return attr  


    def __repr__(self):
        return '<{}({})>'.format(type(self), self.raw)
  


class key(response):
    pass


class package(response):
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
                

    class params:
        action = False
        attachments = False
        payload = False
        command = False
        from_chat = False
        gment = ""
        mentions = []
        key_start = 0
        bot_mentioned = False


    type = None


    def getItems(self):
        return self.items[:-1]
            

    def check(self, command: list) -> typing.Union[bool, list]:
        """
        Following keys:
        $item - any string
        $items - any string
        $expr - expression item
        $exprs - list from this item to the end is a list of expression objects
        $mention - mention item
        $mentions - list from this item to the end is a list of mention objects
        """
        if len(self.items) == 0:
            return False
        
        if command[-1] not in [self.__mentions, self.__exprs, self.__items]:
            if len(command) + 1 != len(self.items): 
                return False

        for i in range(len(command)):
            if command[i] == self.items[i]:
                continue
                
            elif command[i] == self.__item:
                if not isinstance(self.items[i], str):
                    return False

                continue

            elif command[i] == self.__items:
                return self.items[i:-1]

            elif command[i] == self.__expr:
                if not isinstance(self.items[i], (expression, str)):
                    return False

                continue

            elif command[i] == self.__mention:
                if not isinstance(self.items[i], mention):
                    return False

                continue

            elif command[i] == self.__exprs:
                if not isinstance(i, expression):
                    return False

                return self.items[i:-1]

            elif command[i] == self.__mentions:
                mentions = 0
                for j in self.items[i:-1]:
                    if not isinstance(j, (mention, str)):
                        return False
                    mentions += 1

                if mentions > 1:
                    return self.items[i:-1]

                else:
                    return False

            else:
                return False
            
        return True