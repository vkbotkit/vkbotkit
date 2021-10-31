import aiohttp
import asyncio
import six
import threading

from io import IOBase as FileType
from io import BytesIO

from .. import objects

class client_session():
    """
    wrapper over about aiohttp.ClientSession to avoid errors about loops in threads
    headers: dict()
    """

    def __init__(self, *args, **kwargs):
        self.__args = args
        self.__kwargs = kwargs
        self.__sessions = []


    def create_session(self, thread: threading.Thread) -> None:
        if not hasattr(thread, 'session'): 
            thread.session = aiohttp.ClientSession(*self.__args, **self.__kwargs)
            self.__sessions.append(thread.session)


    def __del__(self):
        for session in self.__sessions:
            asyncio.get_event_loop().run_until_complete(session.close())
        

    def __getattr__(self, name):
        if name in dir(aiohttp.ClientSession):
            thread = threading.current_thread()
            self.create_session(thread)
            return getattr(thread.session, name)

class api:
    __slots__ = ('_http', '_method', '_string')

    def __init__(self, http, method, string = None):
        self._http = http
        self._method = method    
        self._string = string


    def __getattr__(self, method):
        self._string = self._string + "." if self._string else ""

        return api(
            self._http, self._method,
            (self._string if self._method else '') + method
        )

    async def __call__(self, **kwargs):
        for k, v in six.iteritems(kwargs):
            if isinstance(v, (list, tuple)):
                kwargs[k] = ','.join(str(x) for x in v)

        return await self._method(self._string, kwargs)

class longpoll:
    def __init__(self, http, method, group_id, log) -> None:
        self.__http = http
        self.__method = method
        self.__group_id = group_id

        self.__url = ""
        self.__key = ""
        self.__ts = 0.0
        self.__wait = 25


    async def __update_longpoll_server(self, update_ts: bool = True) -> None:
        response = await self.__method('groups.getLongPollServer', {'raw': True, 'group_id': self.__group_id})

        if update_ts: 
            self.__ts = response['ts']
        self.__key = response['key']
        self.__url = response['server']


    async def _check(self):
        values = {'act': 'a_check',
                'key': self.__key,
                'ts': self.__ts,
                'wait': self.__wait,
                }
        
        response = await self.__http.get(self.__url, params = values)
        response = await response.json(content_type = None)

        if 'failed' not in response:
            self.__ts = response['ts']

            return response['updates']

        elif response['failed'] == 1:
            self.__ts = response['ts']

        elif response['failed'] == 2:
            await self.__update_longpoll_server(False)

        elif response['failed'] == 3:
            await self.__update_longpoll_server()

        return []


class core:
    def __init__(self, token, group_id, logger):
        self.__token = token
        self.__group_id = group_id
        self.__v = "5.131"

        self.__session = client_session(trust_env=True)
        self._api = api(self.__session, self.__method)
        self._longpoll = longpoll(self.__session, self.__method, group_id, logger)

    @property
    def api_url(self):
        return "https://api.vk.com/method/"

    async def __method(self, method="groups.getById", params = {}):
        request_data = params
        is_raw = request_data.pop("raw", False)
        request_data["access_token"] = self.__token
        request_data["v"] = self.__v

        result = await self.__session.post(self.api_url + method, data = request_data)
        json = await result.json(content_type=None)

        if "response" in json: 
            json = json['response']

        print(json)

        if "error" in json:
            raise Exception("response error")
        
        elif is_raw:
            return json

        else:
            instance = type(json)

            if instance == list:
                return [objects.data.response(i) for i in json]
            
            elif instance == dict:
                return objects.data.response(json)

            else:
                return json

    
    def __repr__(self):
        return f"<testcanarybot.framework._api.core@club{self.__group_id}>"


class uploader:
    __slots__ = ('__api', '__assets')

    def __init__(self, api, assets):
        self.__api = api
        self.__assets = assets


    async def photo_messages(self, photos):
        response = await self.__api.photos.getMessagesUploadServer(peer_id = 0)
        response = await self.__api._http.post(response.upload_url, data = self.convertAsset(photos))
        response = await response.json(content_type = None)

        return await self.__api.photos.saveMessagesPhoto(**response)

        
    async def photo_group_widget(self, photo, image_type):
        response = await self.__api.appWidgets.getGroupImageUploadServer(image_type = image_type)
        response = await self.__api._http.post(response.upload_url, data = self.convertAsset(photo))
        response = await response.json(content_type = None)

        return await self.__api.appWidgets.saveGroupImage(**response)


    async def photo_chat(self, photo, peer_id):
        if peer_id < 2000000000: 
            raise ValueError("Incorrect peer_id")

        values = {
            "chat_id": peer_id - 2000000000,
        }

        response = await self.__api.photos.getChatUploadServer(**values)
        response = await self.__api._http.post(response.upload_url, data = self.convertAsset(photo))
        response = await response.json(content_type = None)

        return await self.__api.messages.setChatPhoto(file = response['response'])


    async def document(self, document, title=None, tags=None, peer_id=None, doc_type = 'doc', to_wall = None):
        values = {
            'peer_id': peer_id,
            'type': doc_type
        }
        
        response = await self.__api.docs.getMessagesUploadServer(**values) # vk.com/dev/docs.getMessagesUploadServer
        response = await self.__api._http.post(response.upload_url, data = self.convertAsset(document, sign = 'file'))
        response = await response.json(content_type = None)

        if title: response['title'] = title 
        if tags: response['tags'] = tags

        return await self.__api.docs.save(**response) 


    async def audio_message(self, audio, peer_id=None):
        return await self.document(audio, doc_type = 'audio_message', peer_id = peer_id)


    async def story(self, file, file_type,
              reply_to_story=None, link_text=None,
              link_url=None):

        if file_type == 'photo':
            method = self.__api.stories.getPhotoUploadServer

        elif file_type == 'video':
            method = self.__api.stories.getVideoUploadServer

        else:
            raise ValueError('type should be either photo or video')

        if (not link_text) != (not link_url):
            raise ValueError(
                'Either both link_text and link_url or neither one are required'
            )

        if link_url and not link_url.startswith('https://vk.com'):
            raise ValueError(
                'Only internal https://vk.com links are allowed for link_url'
            )

        if link_url and len(link_url) > 2048:
            raise ValueError('link_url is too long. Max length - 2048')

        values = dict()

        values['add_to_news'] = True
        if reply_to_story: values['reply_to_story'] = reply_to_story
        if link_text: values['link_text'] = link_text
        if link_url: values['link_url'] = link_url

        response = await method(**values)
        response = await self.__api._http.post(response.upload_url, data = self.convertAsset(file, 'file' if file_type == "photo" else 'video_file'))
        response = await response.json(content_type = None)

        return await self.__api.stories.save(upload_results = response.response.upload_result)


    def convertAsset(self, files, sign = 'file'):
        if isinstance(files, (str, bytes)) or issubclass(type(files), FileType):
            response = None

            if isinstance(files, str): 
                response = self.__assets(files, 'rb', buffering = 0)
            elif isinstance(files, bytes): 
                response = self.__assets(files)
            else:
                response = files

            return {
                sign: response
            }

        elif isinstance(files, list):
            files_dict = {}

            for i in range(min(len(files), 5)): # ограничение в пять файлов
                if isinstance(files[i], (str, bytes)) or issubclass(type(files[i]), FileType):
                    response = None

                    if isinstance(files[i], str): 
                        response = self.__assets(files[i], 'rb', buffering = 0)
                    elif isinstance(files[i], bytes): 
                        response = BytesIO(files[i])
                    else:
                        response = files[i]

                    files_dict[sign + str(i+1)] = response

                else:
                    raise TypeError("Only str, bytes or file-like objects")

            return files_dict

        else:
            raise TypeError("Only str, bytes or file-like objects")

