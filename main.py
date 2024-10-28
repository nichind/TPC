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
        try:
            if self.bot_loop:
                # self.bot_loop.run_until_complete(self.dp.stop_polling())
                self.bot_loop.stop()
                self.bot_loop.close()
        except Exception as exc:
            self.logger.exception(exc)
        self.bot_loop = new_event_loop()
        try:
            self.bot_loop.run_until_complete(create_dp(self))
        except Exception as exc:
            self.logger.exception(exc)

    def exit(self):
        os._exit(-1)
        # if self.tray:
        #     self.pc_handlers.notify('TPC', 'Bye-bye!')
        # self.run_in_loop(self.pc_handlers.on_shutdown)

    def restart(self):
        os.execl(sys.executable, sys.executable, *sys.argv)
        os._exit(-1)


if __name__ == '__main__':
    import psutil, time
    import time
    import os
    import psutil


    def elapsed_since(start):
        return time.strftime("%H:%M:%S", time.gmtime(time.time() - start))


    def get_process_memory():
        process = psutil.Process(os.getpid())
        return process.memory_info().rss



    def track(func):
        def wrapper(*args, **kwargs):
            mem_before = get_process_memory()
            start = time.time()
            result = func(*args, **kwargs)
            elapsed_time = elapsed_since(start)
            mem_after = get_process_memory()
            print("{}: memory before: {:,}, after: {:,}, consumed: {:,}; exec time: {}".format(
                func.__name__,
                mem_before, mem_after, mem_after - mem_before,
                elapsed_time))
            return result
        return wrapper

    @track
    def main():
        tpc = TPC()
        tpc.translator = Translator(tpc)
        tpc.tl = tpc.translator.tl
        tpc.translator.chache_translations()
        tpc.tray = Tray(tpc)
        
        module = glob(resource_path('core/pc/*.py'))
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
        
        tpc.pc_handlers.notify(tpc.tl('STARTING'), tpc.tl('STARTING_DESC'))
        loop = new_event_loop()    
        set_event_loop(loop)
        tpc.loop = loop
        tpc.setup_hook = setup_hook
        tpc.tray.run()
        
    main()
