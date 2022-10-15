"""
Copyright 2022 kensoi
"""

import os
import re
import typing

from .objects import Mention, PATH_SEPARATOR


def dump_mention(text: str) -> Mention:
    """
    Конвертировать текст формата [id1|text] в объект Mention
    """

    if text[0] != "[" or text[-1] != "]":
        raise Exception(f"can't init mention from this text: \"{text}\" ")

    text = text[1:-1]
    obj, key = text.split("|")

    if obj.startswith('id'):
        value = int(obj[2:])
        return Mention(value, key)

    if obj.startswith('club'):
        value = int(obj[4:])
        return Mention(value, key)

    if obj.startswith('public'):
        value = int(obj[6:])
        return Mention(value, key)

    raise TypeError("Invalid page id (should be club, public or id)")


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

    for i in filter(lambda item: item != "", re.split(r'(\[.*\])', text)):
        if i[0] == "[" and i[-1] == "]":
            items.append(dump_mention(i))
            continue

        items.extend(smart_split(i))

    return items


def censor_result(result: str): # copied from jieggii/witless
    """
    цензурировать запрещённые слова
    """

    blacklisted_tokens = [
        "сова никогда не спит",
        "#cинийкит",
        "#рaзбудименяв420",
        "all",
        "everyone",
    ]
    links = remove_duplicates(
        re.findall(r"[^ (){\}\[\]\'\";]+\.[^ (){\}\[\]\'\";]+", result)
    )

    for link in links:
        result = result.replace(link, "[ссылка удалена]")

    for token in blacklisted_tokens:
        result = result.replace(token, "*" * len(token))

    return result
