
import pathlib
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from environs import Env

file_env = pathlib.Path(__file__).parent.joinpath(".env")
# config = configparser.ConfigParser()
# config.read(file_config)




env = Env()
env.read_env(file_env)

SQLALCHEMY_DATABASE_URL = env.str("BASE_URL")


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
