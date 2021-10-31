class MethodError(Exception):
    pass


class LibraryError(Exception):
    pass


class LibraryException(LibraryError):
    pass


class LibraryRewriteError(LibraryError):
    pass


class LibraryReload(LibraryException):
    pass


class CallVoid(LibraryException):
    # raise exceptions.CallVoid(objects.task(package))
    pass


class Quit(LibraryException):
    pass