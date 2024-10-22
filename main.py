import os
import sys
from core import *
from asyncio import new_event_loop, gather, run, get_event_loop, set_event_loop, sleep
from threading import Thread
from platform import system
from os.path import dirname, basename, isfile, join
from glob import glob
from loguru import logger
import subprocess


def get_git_revision_short_hash() -> str:
    return subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode('ascii').strip()


class TPC:
    class PCHandlers:
        pass
    
    try:
        version = get_git_revision_short_hash()
    except Exception:
        version = 'unknown'
    
    tasks = {}
    name = 'tpc'
    resource_path = resource_path
    icon_path = resource_path('assets/ico.gif')
    icon = None
    static_icon = None
    
    system = system().lower()
    pc_handlers = PCHandlers()
    setup_hook = None
    tray = None
    loop = None
    bot = None
    bot_loop = None
    bot_thread = None
    logger = logger
    
    logger.info('Loading translations')
    
    logger.info('Created TPC instance')
    
    def restart_bot(self):
        self.logger.info('Restarting bot')
        if self.bot_loop:
            self.bot_loop.close()
        self.bot_loop = new_event_loop()
        self.bot_loop.run_until_complete(create_dp(self))

    def exit(self):
        os._exit(-1)
        # if self.tray:
        #     self.pc_handlers.notify('TPC', 'Bye-bye!')
        # self.run_in_loop(self.pc_handlers.on_shutdown)

    def restart(self):
        os.execl(sys.executable, sys.executable, *sys.argv)
        os._exit(-1)


if __name__ == '__main__':
    tpc = TPC()
    tpc.translator = Translator(tpc)
    tpc.tl = tpc.translator.tl
    tpc.translator.chache_translations()
    tpc.tray = Tray(tpc)
    
    tpc.pc_handlers = CrossPlatformPCHandlers(tpc)
    tpc.windows_handlers = WindowsPCHandlers(tpc)
    tpc.linux_handlers = LinuxPCHandlers(tpc)
    for method in dir(tpc.__dict__[f'{tpc.system}_handlers']):
        tpc.pc_handlers.__dict__[method] = getattr(tpc.__dict__[f'{tpc.system}_handlers'], method)
    
    tpc.pc_handlers.notify(tpc.tl('STARTING'), tpc.tl('STARTING_DESC'))
    loop = new_event_loop()    
    set_event_loop(loop)
    tpc.loop = loop
    tpc.setup_hook = setup_hook
    tpc.tray.run()
