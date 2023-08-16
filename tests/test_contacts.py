import pytest
from fastapi import status

pytestmark = pytest.mark.order(2)


# ============================ Test Create contact ============================


@pytest.mark.asyncio
async def test_create_contact(client, test_contact):
    with open("token") as f:
        access_token = f.read()

    # Запит на створення контакту з переданим access_token
    response = client.post(
        "/contacts/",
        json=test_contact,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    # Перевірка
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert "id" in data


# ============================== Test get contacts ============================


@pytest.mark.asyncio
async def test_get_contacts(client):
    with open("token") as f:
        access_token = f.read()

    response = client.get(
        "/contacts/",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)


# ============================ Test Remove contact ============================


@pytest.mark.asyncio
async def test_remove_contact(client, test_contact):
    # Отримуємо токен із файлу "token"
    with open("token") as f:
        access_token = f.read()

    # Вказуємо ID контакту, який хочемо видалити
    contact_id = 1

    # Надсилаємо запит на видалення контакту із зазначенням access token
    response = client.delete(
        f"/contacts/{contact_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    # Перевіряємо успішне видалення та відсутність контакту
    assert response.status_code == status.HTTP_200_OK
