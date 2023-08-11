import pytest
from fastapi import status

pytestmark = pytest.mark.order(8)

@pytest.mark.asyncio
async def test_remove_contact(client, test_contact):
    # Отримуємо токен із файлу "token"
    with open("token") as f:
        access_token = f.read()

    # Вказуємо ID контакту, який хочемо видалити
    contact_id = 1

    # Надсилаємо запит на видалення контакту із зазначенням access token
    response = await client.delete(
        f"/contacts/{contact_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    # Перевіряємо успішне видалення та відсутність контакту
    assert response.status_code == status.HTTP_200_OK


