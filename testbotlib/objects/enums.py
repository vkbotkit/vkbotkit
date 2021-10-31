from enum import Enum


class events(Enum):
    message_new = 'message_new'
    message_edit = 'message_edit'
    message_allow = 'message_allow'
    message_typing_state = 'message_typing_state'
    message_reply = 'message_reply'
    message_deny = 'message_deny'
    message_event = 'message_event'
    
    photo_new = 'photo_new'
    photo_comment_new = 'photo_comment_new'
    photo_comment_edit = 'photo_comment_edit'
    photo_comment_restore = 'photo_comment_restore'
    photo_comment_delete = 'photo_comment_delete'

    audio_new = 'audio_new'

    video_new = 'video_new'
    video_comment_new = 'video_comment_new'
    video_comment_edit = 'video_comment_edit'
    video_comment_restore = 'video_comment_restore'
    video_comment_delete = 'video_comment_delete'

    wall_post_new = 'wall_post_new'
    wall_repost = 'wall_repost'
    wall_reply_new = 'wall_reply_new'
    wall_reply_edit = 'wall_reply_edit'
    wall_reply_restore = 'wall_reply_restore'
    wall_reply_delete = 'wall_reply_delete'

    board_post_new = 'board_post_new'
    board_post_edit = 'board_post_edit'
    board_post_restore = 'board_post_restore'
    board_post_delete = 'board_post_delete'

    market_comment_new = 'market_comment_new'
    market_comment_edit = 'market_comment_edit'
    market_comment_restore = 'market_comment_restore'
    market_comment_delete = 'market_comment_delete'
    market_order_new = 'market_order_new'
    market_order_edit = 'market_order_edit'

    group_leave = 'group_leave'
    group_join = 'group_join'

    user_block = 'user_block'
    user_unblock = 'user_unblock'

    poll_vote_new = 'poll_vote_new'

    group_officers_edit = 'group_officers_edit'
    group_change_settings = 'group_change_settings'
    group_change_photo = 'group_change_photo'

    vkpay_transaction = 'vkpay_transaction'
    app_payload = 'app_payload'

    like_add = 'like_add'
    like_remove = 'like_remove'


class action(Enum):
    chat_photo_update = "chat_photo_update"
    chat_photo_remove = "chat_photo_remove"
    chat_create = "chat_create"
    chat_title_update = "chat_title_update"
    chat_invite_user = "chat_invite_user"
    chat_kick_user = "chat_kick_user"
    chat_pin_message = "chat_pin_message"
    chat_unpin_message = "chat_unpin_message"
    chat_invite_user_by_link = "chat_invite_user_by_link"


class values(Enum):
    empty = ''
    log = 'log'
    tumbler = 'tumbler'
    workspace = 'workspace'

    expr = 'expr'


    hidden = '$$$'