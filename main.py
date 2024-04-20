import asyncio
import os
import random
import time
import aiogram.utils.exceptions
from aiogram import types
from aiogram.types import Message, CallbackQuery, BotCommand
from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from tpcc import *
import pystray
from PIL import Image
from dotenv import load_dotenv
from pystray import MenuItem, Menu
import getpass
from threading import Thread
from pathlib import Path

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
            load_dotenv()
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


    def add_to_boot():
        file_path = os.getcwd()
        bat_path = r'C:\Users\%s\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup' % username
        with open(bat_path + '\\' + "tpcc.bat", "w+") as bat_file:
            bat_file.write(r'start /MIN "" %s' % f'{file_path}/run_build.bat')


    def remove_from_boot():
        os.remove(r'C:\Users\%s\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\tpcc.bat' % username)


    def update_token():
        settings = SettingsManagement.get(1)
        new_token = Ask(settings.bot_token, 'TPCC', 'Bot token').fancy(False)
        if new_token:
            SettingsManagement.update(1, bot_token=new_token)


    def change_password():
        settings = SettingsManagement.get(1)
        new_password = Ask(settings.password, 'TPCC', 'Enter preferred bot password').fancy(False)
        if new_password:
            SettingsManagement.update(1, password=new_password)
            for user in asyncio.run(UserManagement.get_all()):
                asyncio.run(UserManagement.update(user.user_id, access=False))


    def refresh_tray():
        while True:
            buttons = []
            buttons.append(MenuItem(text="Bot token", action=update_token, default=True))
            buttons.append(MenuItem(text="Bot password", action=change_password))
            if Path(r'C:\Users\%s\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\tpcc.bat' % username).is_file():
                buttons.append(MenuItem('Dont start on Windows boot', remove_from_boot))
            else:
                buttons.append(MenuItem('Start on Windows boot', add_to_boot))
            buttons.append(MenuItem('Close', close))
            tray.menu = Menu(*buttons)
            time.sleep(0.2)


    Thread(target=refresh_tray).start()
    Thread(target=cycle, args=(tray, 'ico.gif')).start()
    Thread(target=tray.run).start()

    tray.notify('Check your tray icons. Join discord.gg/nichind and t.me/nichindpf')
    while True:
        try:
            executor.start_polling(tg_bot.dp, skip_updates=True, timeout=2)
        except:
            time.sleep(5)
