"""
Copyright 2022 kensoi
"""

class Mention:
    """
    Объект упоминания
    """

    __slots__ = ('value', 'key', 'repr')


    def __init__(self, page_id = None, page_key = None):
        self.value = page_id

        page_type = "id" if page_id > 0 else "public"
        self.key = page_key if page_key else f"@{page_type}{abs(page_id)}"
        self.repr = f"[id{abs(page_id)}|{self.key}]"


    def __int__(self):
        return self.value


    def __str__(self):
        return self.key


    def __repr__(self):
        return self.repr
