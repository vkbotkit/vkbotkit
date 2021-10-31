from . import _features

class bot:
    def __init__(self, token, group_id, enable_dir = False, library_directory = None, logger = None):
        self.sdk = _features.sdk(token, group_id, logger = logger)
        self.library = _features.callbacklib(self.sdk, library_directory)