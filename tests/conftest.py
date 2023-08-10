# tests/conftest.py

import os
import sys
import pytest
import asyncio

from fastapi import Depends, status
from httpx import AsyncClient
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text


# Добавляем папку src в PYTHONPATH
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)


from main import app
from database import get_session, DatabaseSessionManager, Base
from conf import settings

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

sessionmanager = DatabaseSessionManager(SQLALCHEMY_DATABASE_URL)


async def clear_users_table():
    async with sessionmanager.session() as session:
        await session.execute(text('DELETE FROM users'))
        await session.execute(text('DELETE FROM contacts'))
        await session.commit()
        await session.close()

@pytest.hookimpl(tryfirst=True)
def pytest_sessionstart(session):
    asyncio.run(clear_users_table())
    print("Hook pytest_sessionstart was called!")
        
# Dependency
@pytest.fixture(scope="module")
async def overrides_session():
    
    async with sessionmanager.session() as session:
        yield session
        await session.close()  

@pytest.fixture(scope="module")
async def test_user(overrides_session):
    # Создайть тестового пользователя и установите confirmed=True
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
