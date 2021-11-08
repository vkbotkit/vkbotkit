# TESTBOT-NEWVK

## Install Guide:
```bash
$ pip3 install testbot-newvk
```
or

```bash
$ pip3 install https://github.com/kensoi/testbot-newvk/tarball/main/
```

## Set up guide:

```python
from testbotlib import bot
from testbotlib.objects import library_module
import asyncio

loop = asyncio.get_event_loop()

class basic_lib(library_module):
    # paste here commands

async def main():
    bot_test = bot("<token>")
    await bot_test.start_polling()

loop.run_until_complete(main())
```