import pytest
from fastapi import status

pytestmark = pytest.mark.order(6)


@pytest.mark.asyncio
async def test_create_contact(client):
    
    with open("token") as f:
        access_token = f.read()
    
    # Дані для нового контакту
    new_contact_data = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "johndoe@example.com",
        "phone_number": "123456789",
        "birthday": "2000-01-01",
        "additional_data": "Some additional data",
    }

    # Запит на створення контакту з переданим access_token
    response = await client.post(
        "/contacts/",
        json=new_contact_data,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    # Перевірка
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert "id" in data

