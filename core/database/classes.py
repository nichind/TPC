from sqlalchemy import Column, String, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from asyncio import get_event_loop, new_event_loop
from typing import Self


engine = create_async_engine('sqlite+aiosqlite:///./tpc.sqlite?check_same_thread=False')
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
Base = declarative_base()


class Setting(Base):
    __tablename__: str = 'settings'

    key = Column(String, primary_key=True)
    value = Column(JSON)

    def __repr__(self):
        return f'Settings({self.key}={self.value})'

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
        return setting

    @classmethod
    async def update(cls, key: str, value) -> Self:
        async with async_session() as session:
            setting = await cls.get(key=key)
            setting.value = value
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
