# VKBotKit

## Install

```bash
$ pip3 install https://github.com/kensoi/vkbotkit/tarball/dev/
```

## First bot script

```python
from vkbotkit import librabot
from vkbotkit.objects import decorators, filters, enums
import asyncio


class basic_lib(library_module):
    @decorators.callback(filters.whichUpdate({enums.events.message_new,}))
    async def send_hello(self, package):
        await package.toolkit.send_reply(package, "hello world!")


async def main():
    bot = librabot("<token>") # insert here token for your bot instead of <token>
    bot.library.import_module(basic_lib)
    await bot.start_polling()


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
```