import pickle
import pytest
from fastapi import status
from unittest.mock import patch
from services.auth import auth_service
from unittest.mock import MagicMock, patch
from sqlalchemy import select
from database import User
from datetime import date

pytestmark = pytest.mark.order(2)

# ================ Test Create contact by notauthorized user =================


@pytest.mark.asyncio
async def test_create_contact(client, test_contact):
    access_token = "wrong_token"

    with patch.object(auth_service, "r") as redis_mock:
        redis_mock.get.return_value = None

        # Запит на створення контакту з переданим access_token
        response = client.post(
            "/contacts",
            json=test_contact,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        # Перевірка
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        print(data)
        assert data["detail"] == "Could not validate credentials"


# ============================ Test Create contact ============================


@pytest.mark.asyncio
async def test_create_contact(client, test_contact, token):
    access_token = await token

    with patch.object(auth_service, "r") as redis_mock:
        redis_mock.get.return_value = None

        # Запит на створення контакту з переданим access_token
        response = client.post(
            "/contacts",
            json=test_contact,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        # Перевірка
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "id" in data


# ============================== Test get contacts ============================


@pytest.mark.asyncio
async def test_get_contacts(client, token):
    access_token = await token

    with patch.object(auth_service, "r") as redis_mock:
        redis_mock.get.return_value = None
        response = client.get(
            "/contacts/",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        data = response.json()
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(data, list)
        assert data[0]["first_name"] == "John"


# ============================ Test Update contact ============================


@pytest.mark.asyncio
async def test_update_contact(client, test_contact, user, token):
    access_token = await token

    contact_id = 1

    user = User(
        id=1, email=user["email"], password=user["password"], username=user["username"]
    )

    updated_contact_data = {
        "first_name": "UpdatedJohn",
        "last_name": "UpdatedDoe",
        "email": "updatedjohndoe@example.com",
        "phone_number": "987654321",
        "birthday": "2001-01-01",
        "additional_data": "Updated additional data",
    }

    with patch.object(auth_service, "r") as redis_mock:
        redis_mock.get.return_value = pickle.dumps(user)
        response = client.put(
            f"/contacts/{contact_id}",
            json=updated_contact_data,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["first_name"] == updated_contact_data["first_name"]


# ======================= Test get_upcoming_birthdays =========================


@pytest.mark.asyncio
async def test_get_upcoming_birthdays(client, user, token):
    user = User(
        id=1, email=user["email"], password=user["password"], username=user["username"]
    )

    access_token = await token

    with patch.object(auth_service, "r") as redis_mock:
        redis_mock.get.return_value = pickle.dumps(user)
        response = client.get(
            "/contacts/birthdays/365",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)


# ====================== Test Remove unexisting contact =======================


@pytest.mark.asyncio
async def test_remove_unexisting_contact(client, test_contact, user, token):
    access_token = await token

    contact_id = 2

    user = User(
        id=1, email=user["email"], password=user["password"], username=user["username"]
    )

    with patch.object(auth_service, "r") as redis_mock:
        redis_mock.get.return_value = pickle.dumps(user)
        # Надсилаємо запит на видалення контакту із зазначенням access token
        response = client.delete(
            f"/contacts/{contact_id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        # Перевіряємо успішне видалення та відсутність контакту
        assert response.status_code == status.HTTP_404_NOT_FOUND


# ============================ Test Access denied =============================


@pytest.mark.asyncio
async def test_remove_contact_access_denied(
    client, test_contact, user, token, monkeypatch
):
    access_token = await token

    contact_id = 1

    user = User(
        id=3, 
        email=user["email"],
        password=user["password"],
        username=user["username"],
    )

    # Mock the session's `get` method to return the contact
    async def mock_get(*args, **kwargs):
        return Contact(id=1, user_id=1)  # Assuming contact exists

    with patch.object(auth_service, "r") as redis_mock:
        redis_mock.get.return_value = pickle.dumps(user)
        response = client.delete(
            f"/contacts/{contact_id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN


# ============================ Test Remove contact ============================


@pytest.mark.asyncio
async def test_remove_contact(client, test_contact, user, token):
    access_token = await token

    contact_id = 1

    user = User(
        id=1, email=user["email"], password=user["password"], username=user["username"]
    )

    with patch.object(auth_service, "r") as redis_mock:
        redis_mock.get.return_value = pickle.dumps(user)
        # Надсилаємо запит на видалення контакту із зазначенням access token
        response = client.delete(
            f"/contacts/{contact_id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        # Перевіряємо успішне видалення та відсутність контакту
        assert response.status_code == status.HTTP_200_OK
