"""
Copyright 2022 kensoi
"""

class MethodError(Exception):
    """
    Exception
    """


class LibraryError(Exception):
    """
    Exception
    """


class LibraryException(LibraryError):
    """
    Exception
    """


class LibraryRewriteError(LibraryError):
    """
    Exception
    """


class LibraryReload(LibraryException):
    """
    Exception
    """


class CallVoid(LibraryException):
    """
    Exception
    raise exceptions.CallVoid(objects.task(package))
    """


class Quit(LibraryException):
    """
    Exception
    """