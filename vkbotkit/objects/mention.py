"""
Copyright 2022 kensoi
"""


class Mention:
    """
    Объект упоминания
    """

    __slots__ = ('value', 'key', 'repr')


    def __init__(self, page_id = None, page_key = None):
        self.value = int(page_id)

        page_type = "id" if self.value > 0 else "public"
        self.key = page_key if page_key else f"@{page_type}{abs(self.value)}"
        self.repr = f"[{page_type}{abs(self.value)}|{self.key}]"


    def __int__(self):
        return self.value # ID группы, если < 0 или ID пользователя, если > 1


    def __str__(self):
        return self.key  # Название упоминания


    def __repr__(self):
        return self.repr # [{тип страницы}{ID страницы}|{название упоминания}]
