"""
Copyright 2023 kensoi
"""

from io import IOBase, BytesIO


class Uploader:
    """
    Инструменты для работы с медиафайлами
    """

    def __init__(self, assets, api):
        self.assets = assets
        self.api = api


    async def photo_messages(self, photos:list):
        """
        Загрузить фотографии
        """

        response = await self.api.photos.getMessagesUploadServer(peer_id = 0)
        response = await self.api.https.post(response.upload_url,
            data = self.convert_asset(photos))
        response = await response.json(content_type = None)

        image_data = await self.api.photos.saveMessagesPhoto(**response)

        return list(map(lambda photo: f"photo{photo.owner_id}_{photo.id}", image_data))


    async def photo_group_widget(self, photo, image_type):
        """
        Фотография виджета сообщества
        """

        response = await self.api.appWidgets.getGroupImageUploadServer(
            image_type = image_type)
        response = await self.api.https.post(response.upload_url,
            data = self.convert_asset(photo))
        response = await response.json(content_type = None)

        return await self.api.appWidgets.saveGroupImage(**response)


    async def photo_chat(self, photo, peer_id):
        """
        Загрузить новую фотографию беседы
        """

        if peer_id < 2000000000:
            raise ValueError("Incorrect peer_id")

        values = dict(chat_id = peer_id - 2000000000)

        response = await self.api.photos.getChatUploadServer(**values)
        response = await self.api.https.post(response.upload_url,
            data = self.convert_asset(photo))
        response = await response.json(content_type = None)

        return await self.api.messages.setChatPhoto(file = response['response'])


    async def document(self, document, title=None, tags=None,
        peer_id=None, doc_type = 'doc'):
        """
        Загрузить файл для отправки в сообщении
        """

        values = dict(peer_id = peer_id, type = doc_type)

        response = await self.api.docs.getMessagesUploadServer(**values)
        response = await self.api.https.post(response.upload_url,
            data = self.convert_asset(document, sign = 'file'))
        response = await response.json(content_type = None)

        if title:
            response['title'] = title

        if tags:
            response['tags'] = tags

        doc_data = await self.api.docs.save(**response)
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
            method = self.api.stories.getPhotoUploadServer

        elif file_type == 'video':
            method = self.api.stories.getVideoUploadServer

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
        response = await self.api.https.post(response.upload_url,
            data = self.convert_asset(file, 'file' if file_type == "photo" else 'video_file'))
        response = await response.json(content_type = None)

        story_data = await self.api.stories.save(
            upload_results = response.response.upload_result)

        return f"story{story_data.owner_id}_{story_data.id}"


    def convert_asset(self, files, sign = 'file'):
        """
        Вспомогательная функция для работы с файлами из папки assets
        """

        if isinstance(files, (str, bytes)) or issubclass(type(files), IOBase):
            response = None

            if isinstance(files, str):
                response = self.assets(files, 'rb', buffering = 0)

            elif isinstance(files, bytes):
                response = self.assets(files)

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
                        response = self.assets(files[i], 'rb', buffering = 0)

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
        return "<vkbotkit.framework.toolkit.uploader>"
