"""
Copyright 2023 kensoi
"""

from .framework.bot import Bot
from .framework.library import PluginManager
from .framework.longpoll import BotLongpoll
from .objects import VERSION as __version__

__title__ = "vkbotkit"
__author__ = 'kensoi'
__license__ = 'Apache v2'
__copyright__ = 'Copyright 2023 kensoi'
__doc__ = "kensoi/vkbotkit, " + __version__ + """
Documentation is available at kensoi.github.io/vkbotkit
"""

__all__ = ['Bot', "utils"]
