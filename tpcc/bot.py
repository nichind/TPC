import time
import aiogram
from aiogram import executor
import asyncio


class Run:
    def __init__(self):
        pass

    def go(self, tg_bot):
        while True:
            try:
                executor.start_polling(tg_bot.dp, skip_updates=True, timeout=-1)
            except RuntimeError:
                asyncio.set_event_loop(asyncio.new_event_loop())
            except Exception as e:
                print(e)
                time.sleep(5)
