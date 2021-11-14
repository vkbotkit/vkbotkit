import os
import re
import typing
from .objects import path_separator
from .objects.data import mention

# Copyright 2021 kensoi

def convert_path(path: typing.Optional[str] = None, path_type: str = ""):
    path_c = os.getcwd()
    if path:
        if path[0] == '.':
            path_c += path[True:]
        else:
            path_c = path

    return path_separator.join([path_c, path_type])


def filter_folders(libdir):
    files_list = os.listdir(libdir)
    response = []

    for name in files_list:
        obj_path = path_separator.join([libdir, name])
        if os.path.isfile(obj_path):
            if name.endswith(".py"):
                response.append(obj_path)

        elif "__init__.py" in os.listdir(obj_path):
            response.append(path_separator.join([obj_path, "__init__.py"]))
    
    return response


def split_message(text:str):
    '''
    [club195675828|канарейка] помощь -> [<195675828>, 'помощь']
    '''
    copt = text
    REGEX = re.compile(r'\[.*\]', re.MULTILINE)
    splits = REGEX.findall(text)
    result = []

    for join in splits:
        if join.find("|") != -1:
            res = text.split(join, 1)
            if res[0] != '':
                result.extend(smart_split(res[0]))
            result.append(mention(join))
            text = res[1]
    if text != "":
        result.extend(smart_split(text))
    return result


def smart_split(text, split_char = " "):
    if text[0] == " ":
        text = text[1:]
    if text[-1] == " ":
        text = text[:-1]

    res = text.split(split_char)
    return res

