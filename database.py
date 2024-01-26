from typing import AsyncGenerator

from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import select
from sqlalchemy.orm import DeclarativeBase

from models import User

from config import DB_HOST, DB_NAME, DB_PASS, DB_PORT, DB_USER


DATABASE_URL = f'postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}?async_fallback=True'
# DATABASE_URL = f'postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'


engine = create_async_engine(DATABASE_URL)
async_session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_language(id: int, message = Message):
    stmt = select(User.language).where(User.id == id)
    async with async_session_factory() as session:
        async with session.begin():
            try: 
                res = await session.execute(stmt)
                language = res.scalar()
            except Exception:
                raise TypeError
            else:
                return language

