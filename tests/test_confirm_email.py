# tests/test_confirm_email.py

import pytest
from fastapi import status
from pytest_mock import MockFixture

pytestmark = pytest.mark.order(3)


@pytest.mark.asyncio
async def test_confirmed_email(mocker: MockFixture, client, user) -> None:
    mocker.patch(
        "services.auth_service.get_email_from_token", return_value=user["email"]
    )

    user_data = {
        "username": user["username"],
        "email": user["email"],
        "password": user["password"],
        "confirmed": True,
    }
    mocker.patch("repository.get_user_by_email", return_value=user_data)


    response = await client.get(
        f"/users/confirmed_email/some_token"
    ) 

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data == {"message": "Email confirmed"}
