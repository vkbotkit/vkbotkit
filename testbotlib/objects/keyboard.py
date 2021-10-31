from enum import Enum

import json
import six

MAX_BUTTONS_ON_LINE = 5
MAX_DEFAULT_LINES = 10
MAX_INLINE_LINES = 6


def sjson_dumps(*args, **kwargs):
    kwargs['ensure_ascii'] = False
    kwargs['separators'] = (',', ':')

    return json.dumps(*args, **kwargs)


class keyboardcolor(Enum):
    PRIMARY = 'primary' # blue
    SECONDARY = 'secondary' # white
    NEGATIVE = 'negative' # red
    POSITIVE = 'positive' # green


class keyboardbutton(Enum):
    TEXT = "text"
    LOCATION = "location"
    VKPAY = "vkpay"
    VKAPPS = "open_app"
    OPENLINK = "open_link"
    CALLBACK = "callback"


class keyboard:
    __slots__ = ('one_time', 'lines', 'keyboard', 'inline')

    def __init__(self, one_time=False, inline=False):
        self.one_time = one_time
        self.inline = inline
        self.lines = [[]]

        self.keyboard = {
            'one_time': self.one_time,
            'inline': self.inline,
            'buttons': self.lines
        }

    def get_keyboard(self):
        return sjson_dumps(self.keyboard)

    @classmethod
    def get_empty_keyboard(cls):
        keyboard = cls()
        keyboard.keyboard['buttons'] = []
        return keyboard.get_keyboard()

    def add_button(self, label, color=keyboardcolor.SECONDARY, payload=None):
        current_line = self.lines[-1]

        if len(current_line) >= MAX_BUTTONS_ON_LINE:
            raise ValueError(f'Max {MAX_BUTTONS_ON_LINE} buttons on a line')

        color_value = color

        if isinstance(color, keyboardcolor):
            color_value = color_value.value

        if payload is not None and not isinstance(payload, six.string_types):
            payload = sjson_dumps(payload)

        button_type = keyboardbutton.TEXT.value

        current_line.append({
            'color': color_value,
            'action': {
                'type': button_type,
                'payload': payload,
                'label': label,
            }
        })

    def add_callback_button(self, label, color=keyboardcolor.SECONDARY, payload=None):
        current_line = self.lines[-1]

        if len(current_line) >= MAX_BUTTONS_ON_LINE:
            raise ValueError(f'Max {MAX_BUTTONS_ON_LINE} buttons on a line')

        color_value = color

        if isinstance(color, keyboardcolor):
            color_value = color_value.value

        if payload is not None and not isinstance(payload, six.string_types):
            payload = sjson_dumps(payload)

        button_type = keyboardbutton.CALLBACK.value

        current_line.append({
            'color': color_value,
            'action': {
                'type': button_type,
                'payload': payload,
                'label': label,
            }
        })

    def add_location_button(self, payload=None):
        current_line = self.lines[-1]

        if len(current_line) != 0:
            raise ValueError(
                'This type of button takes the entire width of the line'
            )

        if payload is not None and not isinstance(payload, six.string_types):
            payload = sjson_dumps(payload)

        button_type = keyboardbutton.LOCATION.value

        current_line.append({
            'action': {
                'type': button_type,
                'payload': payload
            }
        })

    def add_vkpay_button(self, hash, payload=None):
        current_line = self.lines[-1]

        if len(current_line) != 0:
            raise ValueError(
                'This type of button takes the entire width of the line'
            )

        if payload is not None and not isinstance(payload, six.string_types):
            payload = sjson_dumps(payload)

        button_type = keyboardbutton.VKPAY.value

        current_line.append({
            'action': {
                'type': button_type,
                'payload': payload,
                'hash': hash
            }
        })

    def add_vkapps_button(self, app_id, owner_id, label, hash, payload=None):
        current_line = self.lines[-1]

        if len(current_line) != 0:
            raise ValueError(
                'This type of button takes the entire width of the line'
            )

        if payload is not None and not isinstance(payload, six.string_types):
            payload = sjson_dumps(payload)

        button_type = keyboardbutton.VKAPPS.value

        current_line.append({
            'action': {
                'type': button_type,
                'app_id': app_id,
                'owner_id': owner_id,
                'label': label,
                'payload': payload,
                'hash': hash
            }
        })

    def add_openlink_button(self, label, link, payload=None):
        current_line = self.lines[-1]

        if len(current_line) >= MAX_BUTTONS_ON_LINE:
            raise ValueError(f'Max {MAX_BUTTONS_ON_LINE} buttons on a line')

        if payload is not None and not isinstance(payload, six.string_types):
            payload = sjson_dumps(payload)

        button_type = keyboardbutton.OPENLINK.value

        current_line.append({
            'action': {
                'type': button_type,
                'link': link,
                'label': label,
                'payload': payload
            }
        })

    def add_line(self):
        if self.inline:
            if len(self.lines) >= MAX_INLINE_LINES:
                raise ValueError(f'Max {MAX_INLINE_LINES} lines for inline keyboard')
        else:
            if len(self.lines) >= MAX_DEFAULT_LINES:
                raise ValueError(f'Max {MAX_DEFAULT_LINES} lines for default keyboard')

        self.lines.append([])