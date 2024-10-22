from aiogram import Bot, Dispatcher
from aiogram.utils.token import TokenValidationError
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.exceptions import *
from json import load
from glob import glob
from os.path import dirname, basename, isfile, join, isdir
from os import listdir
from ..util import *
from .handlers import *
import asyncio


async def create_dp(tpc):
    asyncio.set_event_loop(tpc.bot_loop)
    
    token = (await Setting.get(key='bot_token')).value
    
    try:
        bot = Bot(token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    except TokenValidationError:
        tpc.pc_handlers.notify(tpc.tl("FAILED_START_BOT"), tpc.tl("INVALID_TOKEN"))
        tpc.logger.error(f"Invalid token: {token}")
        tpc.bot = None
        return 

    bot.logger = tpc.logger
    bot.tpc = tpc

    dp = Dispatcher(storage=MemoryStorage())
    try:
        pass
    except Exception as exc:
        tpc.logger.error(f'Failed to set bot commands: {exc}')

    module = glob(resource_path('core/bot/handlers/*.py'))
    __all__ = [basename(f)[:-3] for f in module if isfile(f) and not f.endswith('__init__.py')]
    for file in __all__:
        handler = __import__(f'core.bot.handlers.{file}',
                                globals(), locals(), ['CurrentInst'], 0)
        try:
            handler.CurrentInst(bot).setup(dp)
            tpc.logger.success(f"Handler {file} loaded")
        except AttributeError:
            tpc.logger.error(f"Handler {file} has no CurrentInst class or setup method in it, skipping it")
    
    try:
        get_me = (await bot.get_me())
        tpc.logger.success(f"Created Dispatcher for @{get_me.username}, starting polling...")
    except TelegramUnauthorizedError:
        tpc.logger.error(f"Invalid token: {token}")
        await bot.session.close()
        return
    tpc.bot = bot
    tpc.bot.chached_me = get_me.__dict__
    tpc.pc_handlers.notify(tpc.tl("STARTED_BOT"), tpc.tl("STARTED_BOT_TEXT").format(**tpc.bot.chached_me))
    await dp.start_polling(bot)
