import pytest
from fastapi import status
pytestmark = pytest.mark.order(2)

@pytest.mark.asyncio
async def test_create_user(client, user):
    

    response = await client.post("/users/signup", json=user)

    assert response.status_code == status.HTTP_201_CREATED
    assert "user" in response.json()
    assert "detail" in response.json()
    assert response.json()["detail"] == "User successfully created. Check your email for confirmation."
