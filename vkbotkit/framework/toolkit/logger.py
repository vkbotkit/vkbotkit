"""
Copyright 2022 kensoi
"""

import logging
from ...objects.enums import LogLevel


class Log:
    """
    Объект логгера
    """

    def __init__(self) -> None:
        self.__logger = None
        self.__formatter = None
        self.__file_handler = None
        self.log_to_file = False
        self.log_to_terminal = False
        self.log_level = LogLevel.INFO


    def __call__(self, message: str, log_level: LogLevel = LogLevel.INFO):
        if self.__logger:
            self.__logger.log(level = log_level.value, msg = message)

        if self.log_to_file:
            if log_level.value >= self.log_level.value:
                print(f"[{log_level.name}] {message}")


    def __repr__(self):
        return "<vkbotkit.framework.toolkit.log>"


    def configure(self, logger_name: str = "vkbotkit", log_level: LogLevel = LogLevel.INFO,
            log_to_file = False, log_to_terminal = False):
        """
        Настроить логгер
        """

        self.__logger = logging.getLogger(logger_name)
        self.__logger.setLevel(log_level.value)
        self.__formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        self.log_to_file = log_to_file
        self.log_to_terminal = log_to_terminal

        if log_to_file:
            self.__file_handler = logging.FileHandler('.log')
            self.__file_handler.setLevel(log_level.value)
            self.__file_handler.setFormatter(self.__formatter)
            self.__logger.addHandler(self.__file_handler)

        if log_to_terminal:
            self.log_level = log_level
