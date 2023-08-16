import pytest
from fastapi import status
from services.auth import auth_service
from pytest_mock import MockFixture

pytestmark = pytest.mark.order(1)

# =================================== Test root ===============================


def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World!"}


# ================================= Test signup ===============================


def test_create_user(client, user):
    response = client.post("/users/signup", json=user)

    assert response.status_code == status.HTTP_201_CREATED
    assert "user" in response.json()
    assert "detail" in response.json()
    assert (
        response.json()["detail"]
        == "User successfully created. Check your email for confirmation."
    )


# ============================= Test repeat signup ============================


def test_repeat_create_user(client, user):
    response = client.post("/users/signup", json=user)

    assert response.status_code == status.HTTP_409_CONFLICT
    assert "detail" in response.json()
    assert response.json()["detail"] == "Account already exists"


# ======================= Test login not confirmed ============================


@pytest.mark.asyncio
async def test_login_notconfirmed_user(client, credentials, user):
    # Аутентифікація користувача
    response = client.post(
        "/users/login",
        data={"username": credentials["username"], "password": credentials["password"]},
    )

    data = response.json()

    assert "detail" in data
    assert data["detail"] == "Email not confirmed"


# ================================= Test confirm email ========================


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

    response = client.get(f"/users/confirmed_email/some_token")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data == {"message": "Email confirmed"}


# ================================= Test login ================================


@pytest.mark.asyncio
async def test_login_user(client, credentials, user):
    # Аутентифікація користувача
    response = client.post(
        "/users/login",
        data={"username": credentials["username"], "password": credentials["password"]},
    )

    data = response.json()

    with open("token", "w") as f:
        f.write(data["access_token"])

    assert "access_token" in data
    assert (
        await auth_service.get_email_from_token(data["access_token"])
        == credentials["username"]
    )


# ===================== Test login with wrong credentials ====================


@pytest.mark.asyncio
async def test_login_wrong_user(client, credentials, user):
    # Аутентифікація користувача
    response = client.post(
        "/users/login",
        data={"username": credentials["username"], "password": "wrong_pawssword"},
    )

    data = response.json()

    assert data["detail"] == "Invalid password"


# ============================== Test logged user =============================


@pytest.mark.asyncio
async def test_current(client, user):
    with open("token") as f:
        access_token = f.read()

    # Запитуємо маршрут /current з токеном доступу
    response = client.get(
        "/users/current", headers={f"Authorization": f"Bearer {access_token}"}
    )

    # Перевіряємо успішну відповідь
    assert response.status_code == status.HTTP_200_OK
