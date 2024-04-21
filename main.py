import asyncio
import os
import random
import time
import aiogram.utils.exceptions
from tpcc import *
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
        os._exit(0)


    SettingsManagement.add()
    settings = SettingsManagement.get(1)
    if settings.password == 'strong-password':
        SettingsManagement.update(1, password=Ask('', 'TPCC', 'Enter preferred bot password').fancy())

    tray = pystray.Icon('TPCC', Image.open('./ico.gif'), "discord.gg/nichind")


    class AiogramBot:
        def __init__(self):
            while True:
                try:
                    settings = SettingsManagement.get(1)
                    self.bot = Bot(settings.bot_token)
                    self.dp = Dispatcher(self.bot, storage=MemoryStorage())
                    self.thread = None
                    Commands(tray=tray, token=settings.bot_token).setup(self.dp)
                    break
                except aiogram.utils.exceptions.ValidationError:
                    SettingsManagement.update(1, bot_token=Ask(settings.bot_token, 'TPCC', 'Bot token').fancy(False))
            self.connected = False
            self.want_connection = True


    tg_bot = AiogramBot()
    username = getpass.getuser()


    def refresh_tray():
        while True:
            buttons = []
            buttons.append(MenuItem(text="Open", action=App, default=True))
            buttons.append(MenuItem('Close', close))
            tray.menu = Menu(*buttons)
            time.sleep(0.2)


    Thread(target=refresh_tray).start()
    Thread(target=cycle, args=(tray, 'ico.gif')).start()
    Thread(target=tray.run).start()

    Run().go(tg_bot)
