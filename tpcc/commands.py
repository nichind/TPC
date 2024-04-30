import asyncio
import ctypes
import datetime
import random
import time
from threading import Thread
import psutil
import aiogram.utils.exceptions
import pystray
from aiogram import types
from aiogram import Bot, Dispatcher, executor
from aiogram.types import Message, CallbackQuery, BotCommand
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import BoundFilter
from aiogram.dispatcher import FSMContext
from .db import *
import os
import psutil
from mss import mss
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from pynput.keyboard import Controller, KeyCode
from pythonping import ping
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL
from ctypes import cast, POINTER
from winsdk.windows.media.control import GlobalSystemMediaTransportControlsSessionManager as MediaManager


class IsAllowed(BoundFilter):
    async def check(self, message: types.Message) -> bool:
        user = await UserManagement.get(user_obj=message.from_user, user_id=message.from_user.id)
        return user.access


class States(StatesGroup):
    captcha_solving = State()


class Commands:
    def __init__(self, tray: pystray.Icon, token: str):
        self.tray = tray
        self.bot = Bot(token)

    async def start(self, message: Message, state: FSMContext):
        await message.delete()
        await message.bot.set_my_commands(
            [BotCommand('start', 'Main menu'),
             BotCommand('screenshot', 'Get desktop screenshot'),
             BotCommand('media', 'Control media')])
        user = await UserManagement.get(user_obj=message.from_user, user_id=message.from_user.id)
        if ' ' in message.text and user.access == False:
            if message.text.split(' ')[-1] == os.getenv('PASS'):
                await UserManagement.update(user_id=message.from_user.id, access=True)
                user = await UserManagement.get(user_id=message.from_user.id)
        if user.access is False: return

        stats = f"""Hello, {message.from_user.full_name}\n📅 {datetime.datetime.now().strftime("<code>%d/%m/%Y</code>, <code>%H:%M:%S</code>")}"""
        stats += f"""\n\n<b>💻 Stats:</b>\n×\tCPU: <code>{psutil.cpu_percent()}%</code>\n×\tRAM: <code>{(psutil.virtual_memory().used // 1e+9)}GB</code>/<code>{(psutil.virtual_memory().total // 1e+9)}GB</code> (<code>{psutil.virtual_memory().percent}%</code>)"""
        stats += f"""\n×\tPING: <code>{int(ping('google.com').rtt_avg_ms)}ms</code>"""
        stats += f"""\n\n\n<i><code>{str(psutil.Process().memory_info().rss * 0.000001)[0:5]}MB</code></i>"""

        markup = InlineKeyboardMarkup(row_width=3)
        markup.row(InlineKeyboardButton(text='Lock 🔒', callback_data='lock'))
        await message.answer(stats, reply_markup=markup, parse_mode='HTML')

    async def callbacks(self, call: CallbackQuery, state: FSMContext):
        if call.data.startswith('ss:'):
            path = './data/screenshots/' + call.data.split(':')[-1] + '.png'
            await call.message.answer_document(document=open(path, 'rb'))
            await call.answer(text='✅', show_alert=False)
        elif call.data == 'lock':
            os.system('rundll32.exe user32.dll,LockWorkStation')
        elif call.data.startswith('press:'):
            keyboard = Controller()
            if '&' in call.data.split(':')[-1]:
                for key in call.data.split(':')[-1].split('&'):
                    keyboard.press(KeyCode.from_vk(int(key, 0)))
            else:
                keyboard.press(KeyCode.from_vk(int(call.data.split(':')[-1], 0)))
            await call.answer(text='✅', show_alert=False)

    async def screenshot(self, message: Message, state: FSMContext):
        await message.delete()

        date = str(datetime.datetime.now().timestamp()).split(".")[0]
        ss = mss().shot(mon=-1, output=f'./data/screenshots/{date}.png')
        await message.answer_photo(photo=open(ss, 'rb'),
                                   caption=f'''Took this screenshot at 📅 {datetime.datetime.now().strftime("<code>%d/%m/%Y</code>, <code>%H:%M:%S</code>")}\n\n<i>/screenshot</i>''',
                                   parse_mode='HTML',
                                   reply_markup=InlineKeyboardMarkup().row(
                                       InlineKeyboardButton(text='Send as file (full quality)',
                                                            callback_data=f'ss:{date}')))

    async def media_control(self, message: Message, state: FSMContext):
        await message.delete()

        markup = InlineKeyboardMarkup(row_width=3)
        markup.row(InlineKeyboardButton(text='⏮️ Previous', callback_data='press:0xB1'),
                   InlineKeyboardButton(text='⏯️ Play/Pause', callback_data='press:0xB3'),
                   InlineKeyboardButton(text='⏭️ Next', callback_data='press:0xB0'))
        markup.row(InlineKeyboardButton(text='🔉 Volume down', callback_data='press:0xAE'),
                   InlineKeyboardButton(text='🔇 Mute/Unmute', callback_data='press:0xAD'),
                   InlineKeyboardButton(text='🔊 Volume up', callback_data='press:0xAF'))

        async def get_text():
            # Current volume
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            vol = volume.GetMasterVolumeLevelScalar() * 100
            vol_str = f"{vol:.0f}%"

            if int(vol) == 0 or volume.GetMute() == 1:
                emj = "🔇"
            elif int(vol) < 50:
                emj = '🔉'
            else:
                emj = '🔊'

            async def get_media_info():
                sessions = await MediaManager.request_async()

                current_session = sessions.get_current_session()
                if current_session:
                    info = await current_session.try_get_media_properties_async()

                    info_dict = {song_attr: info.__getattribute__(song_attr) for song_attr in dir(info) if
                                 song_attr[0] != '_'}

                    info_dict['genres'] = list(info_dict['genres'])

                    return f'{info_dict["artist"]} — {info_dict["title"]}'
                return f'<i>Nothing</i>'

            return f"""Current volume: {emj} <b>{vol_str}</b>\nNow playing: 🎧 <b>{await get_media_info()}</b>\n\n<i>/media</i> • <i>last update {datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")}</i>"""

        msg = await self.bot.send_message(message.from_user.id, await get_text(), reply_markup=markup,
                                          parse_mode='HTML')

        async def do():
            bot = Bot(SettingsManagement.get(1).bot_token)
            while True:
                try:
                    await bot.edit_message_text(await get_text(), msg.chat.id, msg.message_id, reply_markup=markup,
                                                parse_mode='HTML')
                except aiogram.utils.exceptions.MessageNotModified:
                    pass
                except:
                    return
                await asyncio.sleep(5)

        return
        # Thread(target=asyncio.run, args=(do(),)).start()

    def setup(self, dp: Dispatcher):
        dp.register_message_handler(self.start, content_types=['text'], state='*', commands=['start'])
        dp.register_callback_query_handler(self.callbacks, state='*')
        dp.register_message_handler(self.screenshot, IsAllowed(), content_types=['text'], state='*',
                                    commands=['screenshot', 'ss', 'sc', 'screen', 'sh'])
        dp.register_message_handler(self.media_control, IsAllowed(), content_types=['text'], state='*',
                                    commands=['media', 'mc', 'music'])
