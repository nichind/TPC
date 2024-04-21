import time
import aiogram
from aiogram import executor


class Run:
    def __init__(self):
        pass

    def go(self, tg_bot):
        while True:
            try:
                executor.start_polling(tg_bot.dp, skip_updates=True, timeout=-1)
            except:
                time.sleep(5)
