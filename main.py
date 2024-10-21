import os
from core import *
from asyncio import new_event_loop, gather, run, get_event_loop
from threading import Thread
from platform import system
from os.path import dirname, basename, isfile, join
from glob import glob


class TPC:
    class PCHandlers:
        pass
    
    class Tasks:
        on_startup = None
        run = None
    
    tasks = Tasks()
    name = 'tpc'
    icon_path = './assets/ico.gif'
    icon = None
    
    system = system().lower()
    pc_handlers = PCHandlers()
    tray = None
    loop = get_event_loop()
    
    def exit(self):
        if self.tray:
            self.pc_handlers.notify('TPC', 'Bye-bye!')
        os._exit(0)


if __name__ == '__main__':
    tpc = TPC()
    
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
    
    loop = tpc.loop
    tpc.tray = Tray(tpc)    
    tpc.tasks.on_startup = loop.create_task(on_startup())
    tpc.tasks.run = loop.create_task(tpc.tray.run())
    tasks = [x for x in dir(tpc.tasks) if not x.startswith('__') and x is not None]
    tasks = [tpc.tasks.__dict__[x] for x in tasks]
    # Thread(target=run, args=(tpc.tray.animate(),)).start()
    tpc.pc_handlers.notify('TPC', 'TPC started!')
    loop.run_until_complete(gather(*tasks))
    