"""
Copyright 2023 kensoi
"""

import inspect
import os
import random
import re
import typing

from .objects import Mention, PATH_SEPARATOR
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
        raise Exception(f"can't init mention from this text: \"{text}\" ")

    text = text[1:-1]

    id, key = text.split("|", 1)
    user_type = -1 # 1 is a user, -1 is a community

    if id.startswith('id'):
        user_type = 1
        id = id.replace("id", "", 1)

    elif id.startswith('club') or id.startswith('public'):
        id = id.replace("club", "", 1)
        id = id.replace("public", "", 1)

    else:
        raise TypeError("Invalid page id (should be club, public or id)")

    return Mention(int(id) * user_type, key)


def convert_path(path: typing.Optional[str] = None, path_type: str = "") -> str:
    """
    Получить местоположение папки <path_type>
    """

    path_c = os.getcwd()

    if path:
        path_c += path[path[0] == '.':]

    return PATH_SEPARATOR.join([path_c, path_type])


def parse_path_for_plugins(library_path) -> list:
    """
    Фильтрация + конвертация плагинов в библиотеке бота
    """

    for module_name in os.listdir(library_path):
        module_path = PATH_SEPARATOR.join([library_path, module_name])
        
        if os.path.isfile(module_path):
            if module_name.endswith(".py"):
                yield module_name[:-3]

        if os.path.isdir(module_path):
            if "__init__.py" in os.listdir(module_path):
                yield module_name


def parse_plugin_for_libs(module):
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

    return list(set(array))


def smart_split(text, split_char = " ") -> filter:
    """
    Умное разделение
    """

    return filter(lambda item: item != "", text.split(split_char))

def get_mentions_list(text):
    pattern = re.compile(r'\[.*?\]')
    return [dump_mention(i) for i in pattern.findall(text)]


def convert_command(text:str) -> list:
    """
    Конвертация текста в список ключевых слов
    """

    text_filtered = text.replace("[club", "[public", -1)
    mention_list = get_mentions_list(text)

    for item in mention_list:
        text_filtered = text_filtered.replace(repr(item), "all", 1)
    
    text_splitted = text_filtered.split(" ")

    for index in range(len(text_splitted)):
        if text_splitted[index] == "all":
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
        message = "Unsupported event ({event_type})".format(event_type=event['type'])
        exception = exceptions.UnsupportedEvent
        toolkit_raise(toolkit, message, LogLevel.ERROR, exception)

    package_raw = {}
    package_raw['type'] = event_type

    if event_type is Events.MESSAGE_NEW:
        package_raw.update(event['object']['message'])
        package_raw['items'] = convert_command(censor_result(package_raw.get("text", "")))
        package_raw['params'] = event['object']['client_info']
        package_raw['mentions'] = get_mentions_list(package_raw.get("text", ""))

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

    
def get_callable_list(object, name_list):
    for key in name_list:
        item = getattr(object, key)

        if callable(item):
            yield item

def get_type_list(item_list, needed_type):
    for item in item_list:
        try:
            inited_callback = item()

            if isinstance(inited_callback, needed_type):
                yield inited_callback
            
        except Exception as e:
            pass

def get_library_handlers(library):
    """
    Получить список обработчиков
    """

    if not isinstance(library, Library):
        raise TypeError("library should be instance of vkbotkit.objects.callback.Library")
    

    attribute_name_list = set(dir(library)) - set(dir(Library()))
    callable_list = list(get_callable_list(library, attribute_name_list))
    return list(get_type_list(callable_list, Wrapper))
