from .database import *
import ctypes
import locale


async def setup_hook(tpc):
    tpc.logger.info('Setup hook started')
    
    for key in ['bot_token', 'user_ids', 'boot_with_system', 'icon_path', 'language']:
        await Setting.get(key=key)
    
    try:
        await tpc.pc_handlers.on_startup()
    except Exception as exc:
        tpc.logger.exception(exc)
    
    tpc.logger.info('Setup hook finished')
    