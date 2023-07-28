"""
Copyright 2023 kensoi
"""

import os
from .callback import callback
from .library import Library
from .mention import Mention

PATH_SEPARATOR = "\\" if os.name == 'nt' else "/"
VERSION = "1.3а4"
NAME_CASES = ['nom', 'gen','dat', 'acc', 'ins', 'abl']
