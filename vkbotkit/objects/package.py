"""
Copyright 2023 kensoi
"""

from .data import Response, Key


class ChatPhoto(Key):
    """
    изображение-обложка чата
    """

    photo_50: str
    photo_100: str
    photo_200: str


class Action(Key):
    """
    Информация о сервисном действии с чатом
    """

    type: str
    member_id: int
    text: str
    email: str
    photo: ChatPhoto


class Coordinate(Key):
    """
    координаты места
    """

    latitude: float
    longitude: float


class Place(Key):
    """
    описание места (если оно добавлено)
    """

    id: int
    title: str
    latitude: float
    longitude: float
    created: int
    icon: str
    country: str
    city: str
    showmap: int


class Geo(Key):
    """
    Информация о местоположении
    """

    type: str
    coordinates: list
    place: Place


class Package(Response):
    """
    Объект обработанного уведомления
    """

    important: bool
    is_cropped: bool
    was_listened: bool

    admin_author_id: int
    conversation_message_id: int
    date: int
    from_id: int
    id: int
    members_count: int
    peer_id: int
    pinned_at: int
    random_id: int
    update_time: int

    message_tag: str
    payload: str
    text: str
    ref: str

    items: list
    attachments: list
    fwd_messages: list

    action: Action
    geo: Geo
    keyboard: Key
    reply_message: Key


    def __repr__(self):
        return "<vkbotkit.objects.package>"
