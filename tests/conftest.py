# tests/conftest.py

import os
import sys
import pytest
import asyncio

from fastapi import Depends, status
from httpx import AsyncClient
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text, select
from unittest.mock import MagicMock


# Добавляем папку src в PYTHONPATH
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)


from main import app
from database import get_session, DatabaseSessionManager, Base, User


SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./test.db"


engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = async_sessionmaker(
    autocommit=False, autoflush=False, bind=engine, expire_on_commit=False
)


@pytest.fixture(scope="session", autouse=True)
def init_models_fixture():
    async def init_models():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

    asyncio.run(init_models())


@pytest.fixture(scope="module")
def client():
    async def override_get_session():
        session = TestingSessionLocal()
        try:
            yield session
        except Exception as err:
            print(err)
            await session.rollback()
        finally:
            await session.close()

    app.dependency_overrides[get_session] = override_get_session

    yield TestClient(app)


@pytest.fixture(scope="module")
def user():
    return {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "qwer1234",
    }


@pytest.fixture(scope="module")
def test_contact():
    return {
        "first_name": "John",
        "last_name": "Doe",
        "email": "johndoe@example.com",
        "phone_number": "123456789",
        "birthday": "2000-01-01",
        "additional_data": "Some additional data",
    }


@pytest.fixture(scope="module")
def credentials():
    return {
        "username": "testuser@example.com",
        "password": "qwer1234",
    }


@pytest.fixture()
async def token(client, user, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("routes.auth_routs.send_email", mock_send_email)
    client.post("/users/signup", json=user)

    current_user = select(User).where(User.email == user.get("email"))
    current_user.confirmed = True
    await TestingSessionLocal().commit()
    response = client.post(
        "/users/login",
        data={"username": user.get("email"), "password": user.get("password")},
    )
    data = response.json()
    
    return data["access_token"]


# @pytest.fixture(scope="module")
# def token():
#     with open("token") as f:
#         token = f.read()
#     return token