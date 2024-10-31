from sqlalchemy import Column, String, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from asyncio import get_event_loop, new_event_loop
from typing import Self
from os.path import expanduser
import os


documents_folder = expanduser("~")
tpc_folder = os.path.join(documents_folder, '.config/tpc')
if not os.path.exists(documents_folder + '/.config'):
    os.mkdir(documents_folder + '/.config')
if not os.path.exists(tpc_folder):
    os.mkdir(tpc_folder)
db_path = os.path.join(tpc_folder, 'db.sqlite')
engine = create_async_engine(f'sqlite+aiosqlite:///{db_path}?check_same_thread=False')
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
Base = declarative_base()


class Setting(Base):
    __tablename__: str = 'settings'

    key = Column(String, primary_key=True)
    value = Column(String)

    def __repr__(self):
        return f'<Setting("{self.key}" = "{self.value}")>'

    @classmethod
    async def add(cls, **kwargs) -> bool:
        async with async_session() as session:
            if (await session.execute(select(Setting).filter_by(**kwargs))).scalar() is None:
                setting = Setting(
                    **kwargs
                )
                session.add(setting)
                await session.commit()
        return await cls.get(key=setting.key)

    @classmethod
    async def get(cls, **kwargs) -> Self:
        async with async_session() as session:
            setting = (await session.execute(select(Setting).filter_by(**kwargs))).scalar()
            if setting is None and 'key' in kwargs:
                await cls.add(key=kwargs['key'])
        return setting if setting is not None else (await cls.get(key=kwargs['key']) if 'key' in kwargs else None)

    @classmethod
    async def update(cls, key: str, value: str) -> Self:
        async with async_session() as session:
            setting = (await session.execute(select(Setting).filter_by(key=key))).scalar()
            if setting is None:
                setting = await cls.add(key=key, value=value)
            setattr(setting, 'value', value)
            await session.commit()
        return await cls.get(key=key)
    

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


if get_event_loop() is None:
    loop = new_event_loop()
    loop.run_until_complete(create_tables())
else:
    get_event_loop().run_until_complete(create_tables())
