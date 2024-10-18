from core import *
from asyncio import new_event_loop, gather


if __name__ == '__main__':
    tasks = []
    loop = new_event_loop()
    tasks.append(loop.create_task(on_startup()))
    loop.run_until_complete(gather(*tasks))
    