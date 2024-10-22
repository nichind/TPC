from aiogram.filters import Filter
from aiogram.types import Message, CallbackQuery
from json import loads
from ..util import *


class Authorized(Filter):
    def __init__(self):
        pass

    async def __call__(self, action: Message | CallbackQuery) -> bool:
        users = loads((await Setting.get(key="user_ids")).value)
        if action.from_user.id in users:
            return True
        return False        
        