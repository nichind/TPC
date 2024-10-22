from aiogram import types, Bot, Dispatcher
from aiogram.types import Message, CallbackQuery, InputFile, BufferedInputFile, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.filters import *
from PIL import Image
from io import BytesIO
from ...util import *


class CurrentInst:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.bot_id = bot.id
        self.token = bot.token
        self.tpc = bot.tpc

    async def any_message(self, message: Message, state: FSMContext):
        await message.delete()

    async def any_callback(self, callback: CallbackQuery, state: FSMContext):
        await callback.message.delete()
        
    def setup(self, dp: Dispatcher):
        dp.message.register(self.any_message)
        dp.callback_query.register(self.any_callback)
        