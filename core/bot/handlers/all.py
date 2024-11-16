from aiogram import Bot, Dispatcher
from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher import FSMContext


class CurrentInst:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.bot_id = bot.id
        self.tpc = bot.tpc
        self.filters = bot.filters

    async def any_message(self, message: Message, state: FSMContext):
        await message.answer(self.tpc.tl("YOUR_ID").format(id=message.from_user.id))
        await message.delete()

    async def any_callback(self, callback: CallbackQuery, state: FSMContext):
        await callback.message.delete()

    def setup(self, dp: Dispatcher):
        dp.register_message_handler(self.any_message, self.filters["deauthorized"]())
        dp.register_callback_query_handler(
            self.any_callback, self.filters["deauthorized"]()
        )
