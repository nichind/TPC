from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils.exceptions import *
from glob import glob
from os.path import dirname, basename, isfile, join, isdir
from ..util import *
from .handlers import *
from .filters import Authorized, Deauthorized
import asyncio


async def create_dp(tpc) -> None:
    """
    Creates the bot and the dispatcher, sets up handlers and starts polling.

    :param tpc: The TelegramPC instance
    :type tpc: TelegramPC
    """
    tpc.logger.info('Creating DP...')
    asyncio.set_event_loop(tpc.bot_loop)
    
    token = (await Setting.get(key='bot_token')).value
    
    try:
        bot = Bot(token, parse_mode='HTML')
    except Exception as exc:
        tpc.logger.exception(f'Failed to create bot: {exc}')
        tpc.pc_handlers.notify(tpc.tl("FAILED_START_BOT"), tpc.tl("INVALID_TOKEN"))
        tpc.bot = None
        return 

    bot.logger = tpc.logger
    bot.tpc = tpc
    bot.filters = {
        'authorized': Authorized,
        'deauthorized': Deauthorized
    }

    dp = Dispatcher(bot, storage=MemoryStorage())
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
            tpc.logger.error(f"Handler {file} has no CurrentInst class or setup method in it or it's simply broken... Skipping it")
    
    try:
        get_me = (await bot.get_me())
        tpc.logger.success(f"Created Dispatcher for @{get_me.username}, starting polling...")
    except Exception as exc:
        tpc.logger.exception(f'Failed to get bot info: {exc}')
        await (await bot.get_session()).close()
        return
    
    tpc.bot = bot
    tpc.bot.chached_me = get_me.__dict__['_values']
    tpc.pc_handlers.notify(tpc.tl("STARTED_BOT"), tpc.tl("STARTED_BOT_TEXT").format(**tpc.bot.chached_me))
    tpc.dp = dp
    await dp.start_polling(bot)
