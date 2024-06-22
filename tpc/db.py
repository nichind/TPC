import os
from sqlalchemy import create_engine, Column, Integer, String, Boolean, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func

engine = create_engine(f'sqlite:///{os.getcwd()}/tpc.sqlite?check_same_thread=False')
Base = declarative_base()


class Session(sessionmaker):
    def __new__(cls):
        """Session generator for database operations"""
        return (sessionmaker(bind=engine))()


class User(Base):
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True)
    username = Column(String, default=None)
    access = Column(Boolean, default=0)


class Log(Base):
    __tablename__ = 'logs'

    timestamp = Column(Float, primary_key=True)
    text = Column(String, default=None)
    json = Column(JSON, default=None)


class Settings(Base):
    __tablename__ = 'settings'

    settings_id = Column(Integer, primary_key=True)
    bot_token = Column(String, default=None)
    password = Column(String, default='strong-password')


Base.metadata.create_all(engine)


class UserManagement:
    @classmethod
    async def add(cls, user_obj, **kwargs) -> bool:
        session = Session()

        user = session.query(User).filter_by(user_id=user_obj.id).first()
        if user is not None:
            return False

        user = User(
            user_id=user_obj.id,
            username=user_obj.username,
            **kwargs
        )

        session.add(user)
        session.commit()
        session.close()

        return True

    @classmethod
    async def get(cls, user_obj=None, **kwargs) -> User | None:
        if user_obj is not None: await cls.add(user_obj)
        session = Session()

        user = session.query(User).filter_by(**kwargs).first()

        session.close()

        return user

    @classmethod
    async def get_all(cls, **kwargs) -> list:
        session = Session()

        user = session.query(User).filter_by(**kwargs).all()

        return user

    @classmethod
    async def update(cls, user_id: int, **kwargs):
        session = Session()

        user = session.query(User).filter_by(user_id=user_id).first()

        for key, value in kwargs.items():
            setattr(user, key, value)

        session.commit()
        session.close()

        return user


class SettingsManagement:
    @classmethod
    def add(cls, **kwargs) -> bool:
        session = Session()

        settings = session.query(Settings).filter_by(settings_id=1).first()
        if settings is not None:
            return False

        settings = Settings(
            settings_id=1,
            **kwargs
        )

        session.add(settings)
        session.commit()
        session.close()

        return True

    @classmethod
    def get(cls, settings_id=1, **kwargs) -> Settings | None:
        session = Session()

        settings = session.query(Settings).filter_by(**kwargs).first()

        session.close()

        return settings

    @classmethod
    def update(cls, settings_id: int, **kwargs):
        session = Session()

        settings = session.query(Settings).filter_by(settings_id=settings_id).first()

        for key, value in kwargs.items():
            setattr(settings, key, value)

        session.commit()
        session.close()

        return settings
