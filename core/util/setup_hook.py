from .database import *
import ctypes
import locale


async def setup_hook(tpc):
    tpc.logger.info('Setup hook started')
    
    for key in ['bot_token', 'admin_ids', 'boot_with_system', 'icon_path', 'language']:
        await Setting.get(key=key)
    
    if (await Setting.get(key='language')).value is None:
        windll = ctypes.windll.kernel32
        language = locale.windows_locale[windll.GetUserDefaultUILanguage()]
        await Setting.update(key='language', value=language[:2].upper())
    
    tpc.logger.info('Setup hook finished')
    