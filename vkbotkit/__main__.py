"""
Copyright 2022 kensoi
"""
import sys


PACKAET_SCREEN_NAME = "packaet"
PACKAET_MESSAGE_COVER = "[{screen_name}] {message}"

def message(message_to_print):
    """
    Packaet Logger
    """

    print(PACKAET_MESSAGE_COVER.format(
        screen_name = PACKAET_SCREEN_NAME,
        message = message_to_print))

if __name__ == "__main__":
    args = sys.argv[1:]

    if args[0] == 'test':
        message('hello world!')
