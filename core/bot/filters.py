from aiogram.dispatcher.filters import BoundFilter
from aiogram.types import Message, CallbackQuery
from json import loads
from ..util import Setting


class Authorized(BoundFilter):
    def __init__(self):
        pass

    async def check(self, action: Message | CallbackQuery) -> bool:
        value = (await Setting.get(key="user_ids")).value
        if not value:
            return False
        users = loads(value)
        if action.from_user.id in users:
            return True
        return False


class Deauthorized(BoundFilter):
    def __init__(self):
        pass

    async def check(self, action: Message | CallbackQuery) -> bool:
        value = (await Setting.get(key="user_ids")).value
        if not value:
            return True
        users = loads(value)
        if action.from_user.id not in users:
            return True
        return False
