import asyncio
import time
import aiogram.utils.exceptions
from tpc import *
import pystray
from PIL import Image
from dotenv import load_dotenv
from pystray import MenuItem, Menu
import getpass
from threading import Thread
from pathlib import Path
from aiogram import types
from aiogram.types import Message, CallbackQuery, BotCommand
from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage

if __name__ == '__main__':
    def close():
        os._exit(-1)


    SettingsManagement.add()
    settings = SettingsManagement.get(1)
    if settings.password == 'strong-password':
        SettingsManagement.update(1, password=Ask('', 'TPCC', 'Enter preferred bot password').fancy())

    tray = pystray.Icon('TPC', Image.open('./ico.gif'), "@nichindpf")


    class AiogramBot:
        def __init__(self):
            while True:
                try:
                    settings = SettingsManagement.get(1)
                    if settings.bot_token is None:
                        SettingsManagement.update(1, bot_token=Ask('bot_token', 'TPC', 'Bot token').fancy(False))
                        settings = SettingsManagement.get(1)
                    self.bot = Bot(settings.bot_token)
                    self.dp = Dispatcher(self.bot, storage=MemoryStorage())
                    self.thread = None
                    Commands(tray=tray, token=settings.bot_token).setup(self.dp)
                    break
                except:
                    SettingsManagement.update(1, bot_token=Ask('bot_token', 'TPC', 'Bot token').fancy(False))
            self.connected = False
            self.want_connection = True


    tg_bot = AiogramBot()
    username = getpass.getuser()


    def refresh_tray():
        while True:
            buttons = [MenuItem(text="Open", action=App, default=True), MenuItem('Close', close)]
            tray.menu = Menu(*buttons)
            time.sleep(0.2)


    Thread(target=refresh_tray).start()
    Thread(target=cycle, args=(tray, 'ico.gif')).start()
    Thread(target=tray.run).start()

    notify(f'Started (connected as @{asyncio.run(tg_bot.bot.get_me())["username"]})')
    Run().go(tg_bot)
