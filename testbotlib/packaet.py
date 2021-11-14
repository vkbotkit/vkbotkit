from .objects import path_separator

# Copyright 2021 kensoi

packaet_screen_name = "packaet"
packaet_message_cover = "[{screen_name}] {message}"

def message(message):
    print(packaet_message_cover.format(screen_name = packaet_screen_name, message = message))


def main():
    message("packaet start message")
