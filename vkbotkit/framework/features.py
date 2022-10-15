"""
Copyright 2022 kensoi
"""

import asyncio
import os
import logging
from io import IOBase, BytesIO
from importlib.util import spec_from_file_location, module_from_spec

from .utils import map_folders, convert_command, PATH_SEPARATOR
from ..objects import data, enums, exceptions, LibraryModule


class Assets:
    """
    Рабочий класс для работы с медиафайлами из каталога ассетов.
    """

    def __init__(self, sdk, assets = None):
        if not assets:
            assets = PATH_SEPARATOR.join([os.getcwd(), "assets", ""])

        if assets[-1] != PATH_SEPARATOR:
            assets += PATH_SEPARATOR

        if assets.startswith("."):
            assets = os.getcwd() + assets[1:]

        if not os.path.exists(assets):
            os.mkdir(assets)
            sdk.log(message = "Assets directory was made by framework")

        if not os.path.isdir(assets):
            raise Exception("Assets directory should be a folder")

        self.__path = assets


    def __call__(self, *args, **kwargs):
        args = list(args)

        if len(args) > 0:
            args[0] = self.__path + args[0]

        elif 'file' in kwargs:
            kwargs['file'] = self.__path + kwargs['file']

        encoding = kwargs.pop('encoding') if 'encoding' in kwargs else "utf-8"

        return open(encoding = encoding, *args, **kwargs)


    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def __repr__(self) -> str:
        return "<vkbotkit.features.Assets>"


class CallbackLib:
    """
    Рабочий класс vkbotkit для работы с библиотеками
    """

    def __init__(self, libdir):
        self.__libdir = libdir
        self.handlers = []


    def __repr__(self) -> str:
        return "<vkbotkit.features.CallbackLib>"


    def import_library(self, toolkit):
        """
        Импортировать все плагины из каталога library (либо иного другого)
        """

        if self.__libdir.startswith("."):
            self.__libdir = os.getcwd() + self.__libdir[1:]

        if not os.path.exists(self.__libdir):
            os.mkdir(self.__libdir)

            toolkit.log("library doesn't exist",
                log_level = enums.LogLevel.DEBUG)

            raise exceptions.LibraryExistionError("library doesn't exist")

        if not os.path.isdir(self.__libdir):
            toolkit.log("plugin library folder should be a directory, not a file",
                log_level = enums.LogLevel.DEBUG)

            raise exceptions.LibraryTypeError(
                "plugin library folder should be a directory, not a file")

        for module_path in map_folders(self.__libdir):
            module_root = module_path[len(self.__libdir) + 1:]
            module_name = module_root.replace(PATH_SEPARATOR + "__init__.py", "")

            spec = spec_from_file_location(
                module_path[module_path.rfind(PATH_SEPARATOR)+1:].replace(".py", "", 1),
                module_path)
            loaded_module = module_from_spec(spec)
            spec.loader.exec_module(loaded_module)
            self.import_module(loaded_module.Main)

            toolkit.log(f"Importing plugin {module_name} succeed", enums.LogLevel.DEBUG)

        self.handlers.sort(key = lambda h: h.filter.priority)


    def import_module(self, lib):
        """
        Импортировать специфический модуль
        """

        lib_called = lib()

        if isinstance(lib_called, LibraryModule):
            self.handlers.extend(lib_called.handlers)


    async def parse(self, toolkit, package):
        """
        Обработать уведомление с помощью библиотек
        """

        if not isinstance(package, data.Package):
            package = await self._convert_event(package)

        if not hasattr(package, "toolkit"):
            package.toolkit = toolkit

        if not toolkit.replies.check(package):
            await asyncio.gather(*map(lambda h: h.create_task(package), self.handlers))


    async def _convert_event(self, event):
        """
        Обработать уведомление по типу
        """

        event_type_name = event['type'].upper()

        if not hasattr(enums.Events, event_type_name):
            raise Exception("Unsupported event")

        event_type = getattr(enums.Events, event_type_name)

        if event_type == enums.Events.MESSAGE_NEW:
            package_raw = event['object']['message']
            package_raw['params'] = event['object']['client_info']
            package_raw['items'] = convert_command(package_raw['text'])

        else:
            package_raw = event['object']

        package_raw['type'] = event_type

        return data.Package(package_raw)


class Logger:
    """
    Логгер VKBotKit
    """

    def __init__(
        self, logger_name = None, log_level: enums.LogLevel = enums.LogLevel.INFO,
        file_log = False, print_log = False):
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(log_level.value)
        self.formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        self.file_log = file_log
        self.print_log = print_log

        if file_log:
            self.file_handler = logging.FileHandler('.log')
            self.file_handler.setLevel(log_level.value)
            self.file_handler.setFormatter(self.formatter)
            self.logger.addHandler(self.file_handler)

        if print_log:
            self.log_level = log_level


    def log(self, message: str, log_level: enums.LogLevel = enums.LogLevel.INFO):
        """
        Log message
        """

        self.logger.log(level = log_level.value, msg = message)

        if not self.print_log:
            return

        if log_level.value >= self.log_level.value:
            print(f"[{log_level.name}] {message}")


    def __repr__(self) -> str:
        return "<vkbotkit.features.Logger>"


class Uploader:
    """
    Инструменты для работы с медиафайлами
    """

    __slots__ = ('__toolkit', )

    def __init__(self, toolkit):
        self.__toolkit = toolkit


    async def photo_messages(self, photos:list):
        """
        Загрузить фотографии
        """

        response = await self.__toolkit.api.photos.getMessagesUploadServer(peer_id = 0)
        response = await self.__toolkit.api.https.post(response.upload_url,
            data = self.convert_asset(photos))
        response = await response.json(content_type = None)

        image_data = await self.__toolkit.api.photos.saveMessagesPhoto(**response)

        return list(map(lambda photo: f"photo{photo.owner_id}_{photo.id}", image_data))


    async def photo_group_widget(self, photo, image_type):
        """
        Фотография виджета сообщества
        """

        response = await self.__toolkit.api.appWidgets.getGroupImageUploadServer(
            image_type = image_type)
        response = await self.__toolkit.api.https.post(response.upload_url,
            data = self.convert_asset(photo))
        response = await response.json(content_type = None)

        return await self.__toolkit.api.appWidgets.saveGroupImage(**response)


    async def photo_chat(self, photo, peer_id):
        """
        Загрузить новую фотографию беседы
        """

        if peer_id < 2000000000:
            raise ValueError("Incorrect peer_id")

        values = dict(chat_id = peer_id - 2000000000)

        response = await self.__toolkit.api.photos.getChatUploadServer(**values)
        response = await self.__toolkit.api.https.post(response.upload_url,
            data = self.convert_asset(photo))
        response = await response.json(content_type = None)

        return await self.__toolkit.api.messages.setChatPhoto(file = response['response'])


    async def document(self, document, title=None, tags=None,
        peer_id=None, doc_type = 'doc'):
        """
        Загрузить файл для отправки в сообщении
        """

        values = dict(peer_id = peer_id, type = doc_type)

        response = await self.__toolkit.api.docs.getMessagesUploadServer(**values)
        response = await self.__toolkit.api.https.post(response.upload_url,
            data = self.convert_asset(document, sign = 'file'))
        response = await response.json(content_type = None)

        if title:
            response['title'] = title

        if tags:
            response['tags'] = tags

        doc_data = await self.__toolkit.api.docs.save(**response)
        doc_obj = getattr(doc_data, doc_data.type)

        return f"{doc_data.type}{doc_obj.owner_id}_{doc_obj.id}"


    async def audio_message(self, audio, peer_id=None):
        """
        Загрузить аудиофайл как голосовое сообщение
        """

        return await self.document(audio, doc_type = 'audio_message', peer_id = peer_id)


    async def story(self, file, file_type,
            reply_to_story=None, link_text=None,link_url=None):
        """
        Загрузить историю
        """

        if file_type == 'photo':
            method = self.__toolkit.api.stories.getPhotoUploadServer

        elif file_type == 'video':
            method = self.__toolkit.api.stories.getVideoUploadServer

        else:
            raise ValueError('type should be either photo or video')

        if (not link_text) != (not link_url):
            raise ValueError('Either both link_text and link_url or neither one are required')

        if link_url and not link_url.startswith('https://vk.com'):
            raise ValueError('Only internal https://vk.com links are allowed for link_url')

        if link_url and len(link_url) > 2048:
            raise ValueError('link_url is too long. Max length - 2048')

        values = dict(add_to_news = True)

        if reply_to_story:
            values['reply_to_story'] = reply_to_story

        if link_text:
            values['link_text'] = link_text

        if link_url:
            values['link_url'] = link_url

        response = await method(**values)
        response = await self.__toolkit.api.https.post(response.upload_url,
            data = self.convert_asset(file, 'file' if file_type == "photo" else 'video_file'))
        response = await response.json(content_type = None)

        story_data = await self.__toolkit.api.stories.save(
            upload_results = response.response.upload_result)

        return f"story{story_data.owner_id}_{story_data.id}"


    def convert_asset(self, files, sign = 'file'):
        """
        Вспомогательная функция для работы с файлами из папки assets
        """

        if isinstance(files, (str, bytes)) or issubclass(type(files), IOBase):
            response = None

            if isinstance(files, str):
                response = self.__toolkit.assets(files, 'rb', buffering = 0)

            elif isinstance(files, bytes):
                response = self.__toolkit.assets(files)

            else:
                response = files

            return {
                sign: response
            }

        if isinstance(files, list):
            files_dict = {}

            for i in range(min(len(files), 5)):
                if isinstance(files[i], (str, bytes)) or issubclass(type(files[i]), IOBase):
                    response = None

                    if isinstance(files[i], str):
                        response = self.__toolkit.assets(files[i], 'rb', buffering = 0)

                    elif isinstance(files[i], bytes):
                        response = BytesIO(files[i])

                    else:
                        response = files[i]

                    files_dict[sign + str(i+1)] = response
                    continue

                raise TypeError("Only str, bytes or file-like objects")

            return files_dict

        raise TypeError("Only str, bytes or file-like objects")


    def __repr__(self):
        return "<vkbotkit.api.Uploader>"
