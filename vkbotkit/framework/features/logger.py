"""
Copyright 2022 kensoi
"""

import logging
from ...objects import enums

class Logger:
    """
    Логгер VKBotKit
    """

    def __init__(
        self, logger_name = None, log_level: enums.LogLevel = enums.LogLevel.INFO,
        file_log = False, print_log = False):
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(log_level.value)
        self.formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        self.file_log = file_log
        self.print_log = print_log

        if file_log:
            self.file_handler = logging.FileHandler('.log')
            self.file_handler.setLevel(log_level.value)
            self.file_handler.setFormatter(self.formatter)
            self.logger.addHandler(self.file_handler)

        if print_log:
            self.log_level = log_level


    def log(self, message: str, log_level: enums.LogLevel = enums.LogLevel.INFO):
        """
        Log message
        """

        self.logger.log(level = log_level.value, msg = message)

        if not self.print_log:
            return

        if log_level.value >= self.log_level.value:
            print(f"[{log_level.name}] {message}")


    def __repr__(self) -> str:
        return "<vkbotkit.features.Logger>"
