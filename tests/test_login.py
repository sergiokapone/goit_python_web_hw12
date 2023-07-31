import pytest
from fastapi import status
from services.auth import auth_service

pytestmark = pytest.mark.order(3)


       
@pytest.mark.asyncio
async def test_login_user(client, credentials, test_user):
    # Аутентификация пользователя
    response = await client.post(
        "/users/login",
        data={"username": credentials["username"], "password": credentials["password"]},
    )
    
    print(credentials)

    # Вывод информации об ошибке
    print(response.status_code)
    print(response.text)

    # Проверяем успешную аутентификацию
    # assert response.status_code == status.HTTP_401_UNAUTHORIZED
    data = response.json()
    print(data)
    assert "access_token" in data
    # assert "token_type" in data and data["token_type"] == "bearer"

