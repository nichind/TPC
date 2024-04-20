import asyncio
import datetime
import random
import pystray
from aiogram import types
from aiogram.types import Message, CallbackQuery
from aiogram import Bot, Dispatcher, executor
from aiogram.types import Message, CallbackQuery, BotCommand
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import BoundFilter
from aiogram.dispatcher import FSMContext
from .db import *
import json
from dotenv import load_dotenv
import os
import psutil
from mss import mss
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from pynput.keyboard import Controller, KeyCode
from pythonping import ping


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
        await self.bot.set_my_commands(
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
        await message.answer_photo(photo=open(ss, 'rb'), caption='Your desktop looks like this...', reply_markup=InlineKeyboardMarkup().row(InlineKeyboardButton(text='SEND AS FILE (Full quality)', callback_data=f'ss:{date}')))

    async def media_control(self, message: Message, state: FSMContext):
        markup = InlineKeyboardMarkup(row_width=3)
        markup.row(InlineKeyboardButton(text='Previous ⏮️', callback_data='press:0xB1'), InlineKeyboardButton(text='Play/Pause ⏯️', callback_data='press:0xB3'), InlineKeyboardButton(text='Next ⏭️', callback_data='press:0xB0'))
        markup.row(InlineKeyboardButton(text='Volume down 🔉', callback_data='press:0xAE'), InlineKeyboardButton(text='Mute/Unmute 🔇', callback_data='press:0xAD'), InlineKeyboardButton(text='Volume up 🔊', callback_data='press:0xAF'))
        await message.delete()
        await message.answer('control /media', reply_markup=markup)

    def setup(self, dp: Dispatcher):
        dp.register_message_handler(self.start, content_types=['text'], state='*', commands=['start'])
        dp.register_callback_query_handler(self.callbacks, state='*')
        dp.register_message_handler(self.screenshot, IsAllowed(), content_types=['text'], state='*', commands=['screenshot', 'ss', 'sc', 'screen', 'sh'])
        dp.register_message_handler(self.media_control, IsAllowed(), content_types=['text'], state='*', commands=['media', 'mc', 'music'])
