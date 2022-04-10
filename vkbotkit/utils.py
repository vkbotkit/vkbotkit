"""
Copyright 2022 kensoi
"""

import os
import re
import typing
from .objects import path_separator
from .objects.data import mention

path_separator = "\\" if os.name == 'nt' else "/"

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


def convert_command(text:str) -> list:
    items = []

    for i in filter(lambda item: item != "", re.split(r'(\[.*\])', text)):
        if i[0] == "[" and i[-1] == "]":
            items.append(mention(i))
        
        else:
            items.extend(smart_split(i))

    return items


def smart_split(text, split_char = " ") -> filter:
    return filter(lambda item: item != "", text.split(split_char))