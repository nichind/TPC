from .database import *


async def setup_hook(tpc):
    tpc.logger.info('Setup hook started')
    for key in ['bot_token', 'admin_ids', 'boot_with_system', 'icon_path']:
        await Setting.get(key=key)
    tpc.logger.info('Setup hook finished')
    