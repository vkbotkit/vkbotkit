"""
Copyright 2022 kensoi
"""

from .framework._app import librabot, toolkit
from .framework._api import core

__version__ = "1.0a6"

__title__ = "vkbotkit"
__author__ = 'kensoi'
__license__ = 'Apache v2'
__copyright__ = 'Copyright 2022 kensoi'

__doc__ = "kensoi/vkbotkit, " + __version__ + """
Documentation is available at dshdev.ru/vkbotkit
"""

__all__ = ['librabot', 'core', 'toolkit']