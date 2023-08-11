import pytest
from fastapi import status
from services import auth_service

pytestmark = pytest.mark.order(5)


@pytest.mark.asyncio
async def test_current(client, test_user):
    
    with open("token") as f:
        access_token = f.read()
    
    
    # Запитуємо маршрут /current з токеном доступу
    response = await client.get("/users/current",  headers={f"Authorization": f"Bearer {access_token}"})

    # Перевіряємо успішну відповідь
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
