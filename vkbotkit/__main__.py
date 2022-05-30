import sys

"""
Copyright 2022 kensoi
"""

packaet_screen_name = "packaet"
packaet_message_cover = "[{screen_name}] {message}"

def message(message):
    """
    docstring patch
    """

    print(packaet_message_cover.format(screen_name = packaet_screen_name, message = message))

if __name__ == "__main__":
    args = sys.argv[1:]

    if args[0] == 'test':
        message('hello world!')
