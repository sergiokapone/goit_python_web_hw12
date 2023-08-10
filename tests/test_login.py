import pytest
from fastapi import status
from services.auth import auth_service

pytestmark = pytest.mark.order(4)


       
@pytest.mark.asyncio
async def test_login_user(client, credentials, test_user):
    
    # Аутентифікація користувача
    response = await client.post(
        "/users/login",
        data={"username": credentials["username"], "password": credentials["password"]},
    )
    
    data = response.json()
    
    with open("token", "w") as f:
        f.write(data["access_token"])
        
    assert "access_token" in data
    assert await auth_service.get_email_from_token(data["access_token"]) == credentials["username"]

