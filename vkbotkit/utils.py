"""
Copyright 2023 kensoi
"""

import inspect
import os
import random
import re

from .objects import Mention
from .objects.enums import Action, Events, LogLevel
from .objects.filters import Filter
from .objects.package import Package
from .objects import exceptions

from .objects.library import Library
from .objects.callback.wrapper import Wrapper


def dump_mention(text: str) -> Mention:
    """
    Конвертировать шаблон формата [id1|text] в объект Mention
    """

    if text[0] != "[" or text[-1] != "]":
        raise ValueError(f"can't init mention from this text: \"{text}\" ")

    text = text[1:-1]

    user_id, key = text.split("|", 1)
    user_type = -1 # 1 is a user, -1 is a community

    if user_id.startswith('id'):
        user_type = 1
        user_id = user_id.replace("id", "", 1)

    elif user_id.startswith('club') or user_id.startswith('public'):
        user_id = user_id.replace("club", "", 1)
        user_id = user_id.replace("public", "", 1)

    else:
        raise TypeError("Invalid page id (should be club, public or id)")

    return Mention(int(user_id) * user_type, key)

def parse_path_for_plugins(library_path) -> list:
    """
    Фильтрация + конвертация плагинов в библиотеке бота
    """

    for module_name in os.listdir(library_path):
        module_path = os.path.sep.join([library_path, module_name])

        if os.path.isfile(module_path):
            if module_name.endswith(".py"):
                yield module_name[:-3]

        if os.path.isdir(module_path):
            if "__init__.py" in os.listdir(module_path):
                yield module_name

def parse_plugin_for_libs(module):
    """
    Find vkbotkit.objects.Library at module
    """

    for _, library in inspect.getmembers(module):
        if not inspect.isclass(library):
            continue

        if not issubclass(library, Library):
            continue

        if library == Library:
            continue

        yield library

def remove_duplicates(array):
    """
    Убрать дубликаты
    """

    origin_list = []

    for item in array:
        if item in origin_list:
            continue

        origin_list.append(item)

        yield item

def get_mentions(text):
    """
    get list of mentions at text    
    """
    try:
        pattern = re.compile(r'\[.*?\]')

        for item in pattern.findall(text):
            yield dump_mention(item)
    
    except:
        return []

def convert_command(text:str) -> list:
    """
    Конвертация текста в список ключевых слов
    """

    text_filtered = text.replace("[club", "[public", -1)
    mention_list = list(get_mentions(text))

    for item in mention_list:
        text_filtered = text_filtered.replace(repr(item), "all", 1)

    text_splitted = text_filtered.split(" ")

    for index, item in enumerate(text_splitted, start=0):
        if item == "all":
            text_splitted[index] = mention_list.pop(0)

    return text_splitted

def censor_result(result: str):
    """
    Цензор запрещённых слов ВКонтакте. Скопировано из jieggii/witless
    """

    blacklisted_tokens = [
        "сова никогда не спит",
        "#cинийкит",
        "#рaзбудименяв420",
        "all",
        "everyone",
    ]

    for token in blacklisted_tokens:
        result = result.replace(token, "*" * len(token))

    return result

def censor_links(result:str):
    """
    Цензор ссылок
    """

    list_of_words = re.findall(r"[^ (){\}\[\]\'\";]+\.[^ (){\}\[\]\'\";]+", result)

    for link in remove_duplicates(list_of_words):
        result = result.replace(link, "[ссылка удалена]")

    return result

def convert_to_package(toolkit, event: dict):
    """
    Обработать событие с сервера ВКонтакте в формат Package для внутренней работы фреймворка
    """

    try:
        event_type = Events(event['type'])

    except ValueError:
        message = f"Unsupported event ({event['type']})"
        exception = exceptions.UnsupportedEvent
        toolkit_raise(toolkit, message, LogLevel.ERROR, exception)

    package_raw = {}
    package_raw['type'] = event_type

    if event_type is Events.MESSAGE_NEW:
        package_raw.update(event['object']['message'])
        package_raw['items'] = convert_command(censor_result(package_raw.get("text", "")))
        package_raw['params'] = event['object']['client_info']
        package_raw['mentions'] = list(
            filter(
                lambda item: item.value != toolkit.bot_id, 
                get_mentions(package_raw.get("text", ""))
            )
        )

    else:
        package_raw.update(event['object'])
        package_raw['type'] = event_type

    package = Package(package_raw)
    if event_type is Events.MESSAGE_NEW:
        if "action" in event['object']['message']:
            package.action.type = Action(package.action.type)

    return package

def toolkit_raise(toolkit, message: str, log_level: LogLevel, exception: Exception):
    """
    Вызвать исключение с автоматической записью в лог
    """

    toolkit.log(message, log_level = log_level)
    raise exception(message)

def wrap_filter(check_function):
    """
    Обёртка для простых функций
    """
    if inspect.isclass(check_function):
        raise TypeError("wrap_filter takes only functions")

    if check_function.__code__.co_argcount != 2:
        raise TypeError("wrap_filter takes only functions that \
                        takes only 2 args: toolkit and package")

    wrapped_filter = Filter()
    wrapped_filter.check = check_function

    return wrapped_filter



def gen_random() -> int:
    """
    Сгенерировать случайное число (для messages.send метода)
    """

    return int(random.random() * 999999)

def get_callable_list(parent_object, name_list):
    """
    get list of functions at object
    """

    for key in name_list:
        item = getattr(parent_object, key)

        if callable(item):
            yield item

def get_type_list(item_list, needed_type):
    """
    get list of needed type
    """

    for item in item_list:
        if item.__code__.co_argcount != 1:
            continue

        inited_callback = item()

        if isinstance(inited_callback, needed_type):
            yield inited_callback

def get_attribute_set(parent_object):
    """
    get set of attributes at parent_object
    """

    return set(dir(parent_object))

def get_library_handlers(library):
    """
    Получить список обработчиков
    """

    if not isinstance(library, Library):
        raise TypeError("library should be instance of vkbotkit.objects.callback.Library")

    attribute_name_list = get_attribute_set(library) - get_attribute_set(Library())
    callable_list = get_callable_list(library, attribute_name_list)
    return get_type_list(callable_list, Wrapper)
