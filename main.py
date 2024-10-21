import os
import sys
from core import *
from asyncio import new_event_loop, gather, run, get_event_loop, set_event_loop, sleep
from threading import Thread
from platform import system
from os.path import dirname, basename, isfile, join
from glob import glob
from loguru import logger


class TPC:
    class PCHandlers:
        pass
    
    tasks = {}
    name = 'tpc'
    icon_path = './assets/ico.gif'
    icon = None
    
    system = system().lower()
    pc_handlers = PCHandlers()
    setup_hook = None
    tray = None
    loop = None
    bot = None
    logger = logger
    
    logger.info('Loading translations')
    
    translator = Translator()
    tl = translator.tl
    translator.chache_translations()
    
    logger.info('Created TPC instance')
    
    def exit(self):
        if self.tray:
            self.pc_handlers.notify('TPC', 'Bye-bye!')
        os._exit(0)

    def restart(self):
        os.execl(sys.executable, sys.executable, *sys.argv)
        os._exit(-1)


if __name__ == '__main__':
    tpc = TPC()
    tpc.tray = Tray(tpc)
    
    module = glob(join(dirname(__file__) + '/core/pc', "*.py"))
    __all__ = [basename(f)[:-3] for f in module if isfile(f) and not f.endswith('__init__.py')]
    for file in __all__:
        if file != tpc.system and file != 'crossplatform':
            continue
        handler = __import__(f'core.pc.{file}',
                             globals(), locals(), ['PCHandlers'], 0)
        for attr in dir(handler.PCHandlers):
            if attr.startswith('__'):
                continue
            setattr(tpc.pc_handlers, attr, getattr(handler.PCHandlers(tpc), attr))
    
    loop = new_event_loop()    
    set_event_loop(loop)
    tpc.loop = loop
    tpc.setup_hook = setup_hook
    tpc.tray.run()
