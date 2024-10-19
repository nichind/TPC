from aiogram import Bot, Dispatcher
from aiogram.utils.token import TokenValidationError
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.exceptions import *
from json import load
from loguru import logger
from glob import globt
from os.path import dirname, basename, isfile, join, isdir
from os import listdir
import asyncio


async def create_dp(token: str, tpc):
    cfg = load(open('./config.json', 'r', encoding='utf-8'))
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        bot = Bot(token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    except TokenValidationError:
        return logger.error(f"Invalid token: {token}")

    bot.logger = logger

    dp = Dispatcher(storage=MemoryStorage())
    try:
        await bot.set_my_commands(
            [BotCommand(command=command['name'], description=command['description']) for command in cfg['commands']]
        )
    except Exception as exc:
        logger.error(f'Failed to set bot commands: {exc}')

    for folder in listdir(dirname(__file__) + '/core'):
        if isdir(dirname(__file__) + '/core/' + folder) and folder not in ['__pycache__', 'utils', 'other']:
            module = glob(join(dirname(__file__) + '/core/bot/' + folder, "*.py"))
            __all__ = [basename(f)[:-3] for f in module if isfile(f) and not f.endswith('__init__.py')]
            for file in __all__:
                handler = __import__(f'bot.core.{folder}.{file}',
                                     globals(), locals(), ['CurrentInst'], 0)
                try:
                    handler.CurrentInst(bot).setup(dp)
                except AttributeError:
                    logger.error(f"Handler {folder}/{file} has no CurrentInst class or setup method in it, skipping it")
    try:
        logger.success(f"Created Dispatcher for @{(await bot.get_me()).username}, starting polling...")
    except TelegramUnauthorizedError:
        logger.error(f"Invalid token: {token}")
        await bot.session.close()
        return
    bot.tpc = tpc
    return dp.start_polling(bot)
