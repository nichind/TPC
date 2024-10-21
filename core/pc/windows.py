import ctypes
import locale
from ..util.database import Setting


class PCHandlers:
    def __init__(self, *args, **kwargs):
        pass
    
    @staticmethod
    async def on_startup():
        if (await Setting.get(key='language')).value is None:
            windll = ctypes.windll.kernel32
            language = locale.windows_locale[windll.GetUserDefaultUILanguage()]
            await Setting.update(key='language', value=language[:2].upper())

    @staticmethod
    async def on_shutdown():
        pass
