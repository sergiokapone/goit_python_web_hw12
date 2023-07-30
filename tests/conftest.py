# tests/conftest.py
import pytest
from fastapi import Depends
from httpx import AsyncClient
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

import os
import sys

# Добавляем папку src в PYTHONPATH
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)


from main import app
from database import Base, get_session
from conf import settings

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

# Create an async engine for testing
engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True, future=True)
TestingAsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


@pytest.fixture(scope="module")
async def overrides_session() -> AsyncSession:
    # async with engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.drop_all)
    #     await conn.run_sync(Base.metadata.create_all)

    async with TestingAsyncSessionLocal() as session:
        yield session


@pytest.fixture(scope="module")
async def test_user(overrides_session):
    # Создайте здесь тестового пользователя и установите confirmed=True
    async with overrides_session() as session:
        user_data = {
            "username": "testuser1",
            "email": "testuser1@example.com",
            "password": "qwer1234",
            "confirmed": True,  # Установите поле confirmed=True
        }
        user = User(**user_data)
        session.add(user)
        await session.commit()

        yield user_data  # Возвращает данные пользователя для использования в тестах


@pytest.fixture(scope="module")
def client(overrides_session):
    async def override_get_session():
        return await overrides_session.__anext__()

    app.dependency_overrides[get_session] = override_get_session

    return AsyncClient(app=app, base_url="http://test")


@pytest.fixture(scope="module")
def user():
    return {
        "username": "testuser1",
        "email": "testuser1@example.com",
        "password": "qwer1234",
    }


@pytest.fixture(scope="module")
def credentials():
    return {
        "username": "testuser1@example.com",
        "password": "qwer1234",
    }
