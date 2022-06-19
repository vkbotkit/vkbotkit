"""
Copyright 2022 kensoi
"""

from enum import Enum

class Events(Enum):
    """
    Типы событий для Longpoll
    https://dev.vk.com/method/groups.getLongPollSettings
    """

    MESSAGE_NEW = 'message_new'
    MESSAGE_EDIT = 'message_edit'
    MESSAGE_ALLOW = 'message_allow'
    MESSAGE_TYPING_STATE = 'message_typing_state'
    MESSAGE_REPLY = 'message_reply'
    MESSAGE_DENY = 'message_deny'
    MESSAGE_EVENT = 'message_event'

    PHOTO_NEW = 'photo_new'
    PHOTO_COMMENT_NEW = 'photo_comment_new'
    PHOTO_COMMENT_EDIT = 'photo_comment_edit'
    PHOTO_COMMENT_RESTORE = 'photo_comment_restore'
    PHOTO_COMMENT_DELETE = 'photo_comment_delete'

    AUDIO_NEW = 'audio_new'

    VIDEO_NEW = 'video_new'
    VIDEO_COMMENT_NEW = 'video_comment_new'
    VIDEO_COMMENT_EDIT = 'video_comment_edit'
    VIDEO_COMMENT_RESTORE = 'video_comment_restore'
    VIDEO_COMMENT_DELETE = 'video_comment_delete'

    WALL_POST_NEW = 'wall_post_new'
    WALL_REPOST = 'wall_repost'
    WALL_REPLY_NEW = 'wall_reply_new'
    WALL_REPLY_EDIT = 'wall_reply_edit'
    WALL_REPLY_RESTORE = 'wall_reply_restore'
    WALL_REPLY_DELETE = 'wall_reply_delete'

    BOARD_POST_NEW = 'board_post_new'
    BOARD_POST_EDIT = 'board_post_edit'
    BOARD_POST_RESTORE = 'board_post_restore'
    BOARD_POST_DELETE = 'board_post_delete'

    MARKET_COMMENT_NEW = 'market_comment_new'
    MARKET_COMMENT_EDIT = 'market_comment_edit'
    MARKET_COMMENT_RESTORE = 'market_comment_restore'
    MARKET_COMMENT_DELETE = 'market_comment_delete'
    MARKET_ORDER_NEW = 'market_order_new'
    MARKET_ORDER_EDIT = 'market_order_edit'

    GROUP_LEAVE = 'group_leave'
    GROUP_JOIN = 'group_join'

    USER_BLOCK = 'user_block'
    USER_UNBLOCK = 'user_unblock'

    POLL_VOTE_NEW = 'poll_vote_new'

    GROUP_OFFICERS_EDIT = 'group_officers_edit'
    GROUP_CHANGE_SETTINGS = 'group_change_settings'
    GROUP_CHANGE_PHOTO = 'group_change_photo'

    VKPAY_TRANSACTION = 'vkpay_transaction'
    APP_PAYLOAD = 'app_payload'

    LIKE_ADD = 'like_add'
    LIKE_REMOVE = 'like_remove'


class Action(Enum):
    """
    Типы событий в беседе
    https://dev.vk.com/api/user-long-poll/getting-started#Вложения%20и%20дополнительные%20данные
    """
    
    CHAT_PHOTO_UPDATE = "chat_photo_update"
    CHAT_PHOTO_REMOVE = "chat_photo_remove"
    CHAT_CREATE = "chat_create"
    CHAT_TITLE_UPDATE = "chat_title_update"
    CHAT_INVITE_USER = "chat_invite_user"
    CHAT_KICK_USER = "chat_kick_user"
    CHAT_PIN_MESSAGE = "chat_pin_message"
    CHAT_UNPIN_MESSAGE = "chat_unpin_message"
    CHAT_INVITE_USER_BY_LINK = "chat_invite_user_by_link"


class LogLevel(Enum):
    """
    Уровень логгирования
    """

    CRITICAL = 50
    ERROR = 40
    WARNING = 30
    INFO = 20
    DEBUG = 10
    NOTSET = 0


class NameCases(Enum):
    """
    Падежи имён для ФИО пользователей
    """

    NOM = 'nom'
    GEN = 'gen'
    DAT = 'dat'
    ACC = 'acc'
    INS = 'ins'
    ABL = 'abl'


class KeyboardColor(Enum):
    """
    Доступные цвета кнопок на клавиатуре
    https://dev.vk.com/api/bots/development/keyboard
    """

    PRIMARY = 'primary' # blue
    SECONDARY = 'secondary' # white
    NEGATIVE = 'negative' # red
    POSITIVE = 'positive' # green


class KeyboardButton(Enum):
    """
    Доступные типы кнопок на клавиатуре
    https://dev.vk.com/api/bots/development/keyboard
    """

    TEXT = "text"
    LOCATION = "location"
    VKPAY = "vkpay"
    VKAPPS = "open_app"
    OPENLINK = "open_link"
    CALLBACK = "callback"
