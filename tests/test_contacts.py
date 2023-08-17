import pickle
import pytest
from fastapi import status
from unittest.mock import patch
from services.auth import auth_service
from unittest.mock import MagicMock, patch
from sqlalchemy import select
from database import User

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
        assert data[0]['first_name'] == 'John'

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
