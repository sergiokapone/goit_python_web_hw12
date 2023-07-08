

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from conf.config import settings


SQLALCHEMY_DATABASE_URL = settings.sqlalchemy_database_url

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=True,
    future=True,
)


async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


# Dependency
async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session
