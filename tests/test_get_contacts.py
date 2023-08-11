import pytest
from fastapi import status

pytestmark = pytest.mark.order(7)


@pytest.mark.asyncio
async def test_get_contacts(client):

    with open("token") as f:
        access_token = f.read()


    # Отправьте запрос на создание контакта с переданным access_token
    response = await client.get(
        "/contacts/",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    # Проверьте успешный ответ
    assert response.status_code == status.HTTP_200_OK

