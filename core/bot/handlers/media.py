from aiogram import Bot, Dispatcher
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from aiogram.dispatcher import FSMContext
from datetime import datetime
from asyncio import sleep


class CurrentInst:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.bot_id = bot.id
        self.tpc = bot.tpc
        self.filters = bot.filters

    async def message_constructor(self) -> str:
        async def get_text():
            info_dict = await self.tpc.pc_handlers.get_playing_media()
            if info_dict:
                return f'{info_dict["artist"]} — {info_dict["title"]}'
            return self.tpc.tl("MEDIA_NOTHING")

        text = self.tpc.tl("MEDIA_TEXT").format(
            text=await get_text(),
            date=datetime.now().strftime(
                "<code>%d/%m/%Y</code>, <code>%H:%M:%S</code>"
            ),
        )
        return text

    async def media_control(self, message: Message, state: FSMContext):
        await message.delete()
        markup = InlineKeyboardMarkup(row_width=3)
        markup.row(
            InlineKeyboardButton(
                text=self.tpc.tl("MEDIA_PREVIOUS"), callback_data="media:0xB1"
            ),
            InlineKeyboardButton(
                text=self.tpc.tl("MEDIA_PAUSE"), callback_data="media:0xB3"
            ),
            InlineKeyboardButton(
                text=self.tpc.tl("MEDIA_NEXT"), callback_data="media:0xB0"
            ),
        )
        markup.row(
            InlineKeyboardButton(
                text=self.tpc.tl("MEDIA_VOLDOWN"), callback_data="media:0xAE"
            ),
            InlineKeyboardButton(
                text=self.tpc.tl("MEDIA_MUTE"), callback_data="media:0xAD"
            ),
            InlineKeyboardButton(
                text=self.tpc.tl("MEDIA_VOLUP"), callback_data="media:0xAF"
            ),
        )

        await self.bot.send_message(
            message.from_user.id, await self.message_constructor(), reply_markup=markup
        )

    async def update_message(self, call: CallbackQuery, state: FSMContext):
        await self.tpc.pc_handlers.press(call.data.split(":")[1])
        await sleep(0.0)
        await call.answer()
        await call.message.edit_text(
            await self.message_constructor(), reply_markup=call.message.reply_markup
        )

    def setup(self, dp: Dispatcher):
        dp.register_message_handler(
            self.media_control, self.filters["authorized"](), commands=["media"]
        )
        dp.register_callback_query_handler(
            self.update_message, self.filters["authorized"](), text_contains="media:"
        )
