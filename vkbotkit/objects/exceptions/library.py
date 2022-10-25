"""
Copyright 2022 kensoi
"""

class LibraryError(Exception):
    """
    Ошибка, связанная с библиотекой VKBotKit
    """


class LibraryTypeError(LibraryError):
    """
    Ошибка, вызванная, если указанный адрес библиотеки ссылается на файл, а не каталог
    """


class LibraryExistionError(LibraryError):
    """
    Ошибка, вызванная, если указанный адрес библиотеки ссылается на несуществующий каталог
    """


class LibraryException(LibraryError):
    """
    Exception
    """


class Quit(LibraryException):
    """
    Исключение выхода из Longpoll прослушивания, вызванное функцией toolkit.stop_polling()
    """
