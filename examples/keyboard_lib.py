from vkbotkit.objects import decorators, filters, enums, library_module
from vkbotkit.objects.keyboard import *

"""
Copyright 2022 kensoi
"""

class Main(library_module):
    async def start(self, toolkit):
        self.keyboardTest = keyboard(one_time = False, inline = True)
        self.keyboardTest2 = keyboard(one_time = False, inline = True)

        self.keyboardTest.add_button("канари помощь", keyboardcolor.PRIMARY)
        self.keyboardTest.add_line()
        self.keyboardTest.add_button("Test1")
        self.keyboardTest.add_button("Test2")
        self.keyboardTest.add_line()
        self.keyboardTest.add_button("Test3")
        
        self.keyboardTest2.add_button("тесто", keyboardcolor.PRIMARY)
        self.keyboardTest2.add_line()
        self.keyboardTest2.add_location_button()

    @decorators.callback(filters.whichUpdate({enums.events.message_new,}))
    async def send_hello(self, package):
        await package.toolkit.api.messages.send(
            random_id = package.toolkit.gen_random(),
            peer_id = package.peer_id,
            message = "Пример клавиатуры",
            keyboard = self.keyboardTest.get_keyboard()
        )