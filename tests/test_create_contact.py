import pytest
from fastapi import status

pytestmark = pytest.mark.order(6)


@pytest.mark.asyncio
async def test_create_contact(client, test_contact):
    
    with open("token") as f:
        access_token = f.read()
    
    # Запит на створення контакту з переданим access_token
    response = await client.post(
        "/contacts/",
        json=test_contact,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    # Перевірка
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert "id" in data

