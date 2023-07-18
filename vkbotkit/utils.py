"""
Copyright 2022 kensoi
"""

import os
import random
import re
import typing


from .objects import Mention, PATH_SEPARATOR
from .objects.enums import Action, Events, LogLevel
from .objects.filters import Filter
from .objects.package import Package
from .objects import exceptions


def dump_mention(text: str) -> Mention:
    """
    Конвертировать шаблон формата [id1|text] в объект Mention
    """

    if text[0] != "[" or text[-1] != "]":
        raise Exception(f"can't init mention from this text: \"{text}\" ")

    text = text[1:-1]
    obj, key = text.split("|")

    if obj.startswith('id'):
        value = 2

    elif obj.startswith('club'):
        value = 4

    elif obj.startswith('public'):
        value = 6

    else:
        raise TypeError("Invalid page id (should be club, public or id)")

    return Mention(int(obj[value:]), key)


def convert_path(path: typing.Optional[str] = None, path_type: str = "") -> str:
    """
    Получить местоположение папки <path_type>
    """

    path_c = os.getcwd()

    if path:
        path_c += path[path[0] == '.':]

    return PATH_SEPARATOR.join([path_c, path_type])


def map_folders(libdir) -> list:
    """
    Фильтрация + конвертация плагинов в библиотеке бота
    """

    files_list = os.listdir(libdir)

    def name_filter(name):
        obj_path = PATH_SEPARATOR.join([libdir, name])

        if os.path.isfile(obj_path):
            if name.endswith(".py"):
                return obj_path

        elif "__init__.py" in os.listdir(obj_path):
            return PATH_SEPARATOR.join([obj_path, "__init__.py"])

    filtered_names = map(name_filter, files_list)
    removed_empty_items = filter(lambda x: x is not None, filtered_names)

    return list(removed_empty_items)


def remove_duplicates(array):
    """
    Убрать дубликаты
    """

    return list(set(array))


def smart_split(text, split_char = " ") -> filter:
    """
    Умное разделение
    """

    return filter(lambda item: item != "", text.split(split_char))


def convert_command(text:str) -> list:
    """
    Конвертация текста в список ключевых слов
    """

    items = []
    text_filtered = filter(lambda item: item != "", re.split(r'(\[.*\])', text))

    for i in text_filtered:
        if i[0] == "[" and i[-1] == "]" and "|" in i:
            items.append(dump_mention(i))

        else:
            items.extend(smart_split(i))

    return items


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

    links = remove_duplicates(
        re.findall(r"[^ (){\}\[\]\'\";]+\.[^ (){\}\[\]\'\";]+", result)
    )

    for link in links:
        result = result.replace(link, "[ссылка удалена]")

    return result


async def convert_to_package(toolkit, event: dict):
    """
    Обработать событие с сервера ВКонтакте в формат Package для внутренней работы фреймворка
    """

    try:
        event_type = Events(event['type'])

    except ValueError:
        message = "Unsupported event"
        exception = exceptions.UnsupportedEvent
        toolkit_raise(toolkit, message, LogLevel, exception)

    package_raw = {}
    package_raw['type'] = event_type

    if event_type is Events.MESSAGE_NEW:
        package_raw.update(event['object']['message'])
        package_raw['items'] = convert_command(censor_result(package_raw['text']))
        package_raw['params'] = event['object']['client_info']

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

    def decorator(**kwargs):
        wrapped_filter = Filter()
        wrapped_filter.__dict__.update(kwargs)
        wrapped_filter.check = check_function

        return wrapped_filter

    return decorator


def gen_random() -> int:
    """
    Сгенерировать случайное число (для messages.send метода)
    """

    return int(random.random() * 999999)
