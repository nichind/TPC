from .database import *


async def on_startup():
    for key in ['bot_token', 'admin_ids', 'boot_with_system', 'icon_path']:
        await Setting.get(key=key)
    