"""
Copyright 2023 kensoi
"""


class BotLongpoll:
    """
    Объект для прослушки VK Bots Longpoll
    """

    def __init__(self, bot) -> None:
        self._https = bot.session
        self._method = bot.method
        self.is_polling = False

        self.__url = ""
        self.__key = ""
        self.__ts = 0.0
        self.__wait = 25
        self.__rps_delay = 0


    async def update_server(self, group_id: int, update_ts: bool = True) -> None:
        """
        Обновить сервер
        """

        data = {'raw': True, 'group_id': group_id}
        response = await self._method('groups.getLongPollServer', data)

        if update_ts:
            self.__ts = response['ts']
        self.__key = response['key']
        self.__url = response['server']


    async def check(self, group_id: int) -> list:
        """
        Запросить уведомления с сервера
        """

        values = {
            'act': 'a_check',
            'key': self.__key,
            'ts': self.__ts,
            'wait': self.__wait,
            'rps_delay': self.__rps_delay
        }

        response = await self._https.get(self.__url, params = values)
        response = await response.json(content_type = None)

        if 'failed' not in response:
            self.__ts = response['ts']

            return response['updates']

        if response['failed'] == 1:
            self.__ts = response['ts']

        elif response['failed'] == 2:
            await self.update_server(group_id, False)

        elif response['failed'] == 3:
            await self.update_server(group_id)

        return []


    def __repr__(self):
        return "<vkbotkit.framework.longpoll>"
