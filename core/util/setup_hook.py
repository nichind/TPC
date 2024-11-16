from core.util.database import Setting


async def setup_hook(tpc):
    tpc.logger.info("Setup hook started")

    for key in ["bot_token", "user_ids", "start_on_boot", "icon_path", "language"]:
        await Setting.get(key=key)

    try:
        await tpc.pc_handlers.on_startup()
    except Exception as exc:
        tpc.logger.exception(exc)

    await Setting.update("start_on_boot", tpc.pc_handlers.check_autostart())

    tpc.logger.info("Setup hook finished")
