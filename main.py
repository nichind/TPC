from core import *
from asyncio import new_event_loop, gather
from platform import system
from os.path import dirname, basename, isfile, join
from glob import glob


class TPC:
    class PCHandlers:
        pass
    
    name = 'tpc'
    icon = './ico.svg'
    
    system = system().lower()
    pc_handlers = PCHandlers()
    tray = None


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
    
    tasks = []
    loop = new_event_loop()
    
    tpc.tray = Tray(tpc)
    tpc.icon = tpc.icon
    
    tpc.on_startup = loop.create_task(on_startup())
    tasks.append(loop.create_task(tpc.pc_handlers.notify('TPC', 'TPC started!')))
    tpc.tray.animate = loop.create_task(tpc.tray.animate())
    tpc.tray.run_task = loop.create_task(tpc.tray.run())
    tasks += [tpc.on_startup, tpc.tray.animate, tpc.tray.run_task]
    loop.run_until_complete(gather(*tasks))
    