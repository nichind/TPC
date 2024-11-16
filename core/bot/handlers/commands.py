from aiogram import Bot, Dispatcher
from aiogram.types import (
    Message,
    CallbackQuery,
    InputFile,
)
from aiogram.dispatcher import FSMContext
from datetime import datetime
import psutil


class CurrentInst:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.bot_id = bot.id
        self.tpc = bot.tpc
        self.filters = bot.filters

    async def press_callback(self, call: CallbackQuery, state: FSMContext):
        await call.answer("✅")
        await self.tpc.pc_handlers.press(call.data.split("!")[0].split(":")[1])

    async def start(self, message: Message, state: FSMContext):
        await message.delete()

        await message.answer(
            self.tpc.tl("START_TEXT").format(
                name=message.from_user.full_name,
                date=datetime.now().strftime(
                    "<code>%d/%m/%Y</code>, <code>%H:%M:%S</code>"
                ),
                cpu=psutil.cpu_percent(),
                ram_used=(psutil.virtual_memory().used // 1e9),
                ram_total=(psutil.virtual_memory().total // 1e9),
                ram_percent=psutil.virtual_memory().percent,
                usage=str(psutil.Process().memory_info().rss * 0.000001)[0:5],
            ),
            parse_mode="HTML",
        )

    async def restart(self, message: Message, state: FSMContext):
        await message.delete()
        self.tpc.restart()

    async def screenshot(self, message: Message, state: FSMContext):
        await message.delete()
        await self.bot.send_photo(
            message.chat.id,
            InputFile(
                await self.tpc.pc_handlers.screenshot(),
                filename=datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".png",
            ),
            caption=self.tpc.tl("SCREENSHOT_TEXT"),
        )
        await self.bot.send_document(
            message.chat.id,
            InputFile(
                await self.tpc.pc_handlers.screenshot(),
                filename=datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".png",
            ),
        )

    async def lock(self, message: Message, state: FSMContext):
        await message.delete()
        await self.tpc.pc_handlers.lock()
        await message.answer(self.tpc.tl("LOCK_TEXT"))

    def setup(self, dp: Dispatcher):
        dp.register_callback_query_handler(
            self.press_callback, self.filters["authorized"](), text_contains="press:"
        )
        dp.register_message_handler(
            self.start, self.filters["authorized"](), commands=["start"]
        )
        dp.register_message_handler(
            self.screenshot, self.filters["authorized"](), commands=["screenshot"]
        )
        dp.register_message_handler(
            self.lock, self.filters["authorized"](), commands=["lock"]
        )
