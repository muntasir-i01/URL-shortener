import os

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from decouple import config

DATABASE_URL = config("DATABASE_URL", default="postgresql+asyncpg://shortener:shortener@localhost:5432/shortener")

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, expire_on_commit=False)


async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session
