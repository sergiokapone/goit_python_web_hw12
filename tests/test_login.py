import pytest
from fastapi import status
from services.auth import auth_service

@pytest.mark.asyncio
async def test_login_user(client, credentials):
    # Аутентификация пользователя
    response = await client.post(
        "/users/login",
        data={"username": credentials["username"], "password": credentials["password"]},
    )

    # Проверяем успешную аутентификацию
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data and data["token_type"] == "bearer"

