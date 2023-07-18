"""
Copyright 2022 kensoi
"""

import os
from .callback import Library, callback
from .mention import Mention

PATH_SEPARATOR = "\\" if os.name == 'nt' else "/"
VERSION = "1.2a8"
NAME_CASES = ['nom', 'gen','dat', 'acc', 'ins', 'abl']
