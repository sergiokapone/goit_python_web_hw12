"""
Файл `users.py` містить функції, пов'язані з операціями користувачів, такі як
тримання користувача за електронною поштою, створення нового користувача та
новлення токену оновлення для користувача.
"""

from datetime import datetime
from libgravatar import Gravatar

from fastapi import Depends

from sqlalchemy import select
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession


from database import get_session
from database import User

from services.auth import auth_service

from schemas import UserModel


async def get_user_by_email(email: str, session: AsyncSession) -> User | None:
    """
    Отримує об'єкт користувача за електронною поштою.

    Parameters:
        email (str): Електронна пошта користувача.
        session (AsyncSession): Об'єкт сесії бази даних.

    Returns:
        User: Об'єкт користувача, якщо знайдено, або None, якщо не знайдено.

    """
    try:
        result = await session.execute(select(User).filter(User.email == email))
        user = result.scalar_one_or_none()
        return user
    except NoResultFound:
        return None


async def create_user(body: UserModel, session: AsyncSession) -> User:
    """
    Створює нового користувача.

    Parameters:
        body (UserModel): Модель користувача, що містить дані для створення користувача.
        session (AsyncSession): Об'єкт сесії бази даних.

    Returns:
        User: Об'єкт створеного користувача.

    """
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as e:
        print(e)

    refresh_token = await auth_service.create_refresh_token({"sub": body.email})

    new_user = User(
        username=body.username,
        email=body.email,
        password=body.password,
        created_at=datetime.now(),
        avatar=avatar,
        refresh_token=refresh_token,
    )

    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    return new_user


async def update_token(user: User, token: str | None, session: AsyncSession) -> None:
    """
    Оновлює токен оновлення для користувача.

    Parameters:
        user (User): Об'єкт користувача.
        token (str | None): Токен оновлення або None, якщо токен не вказаний.
        session (AsyncSession): Об'єкт сесії бази даних.

    """
    user.refresh_token = token
    await session.commit()


async def confirmed_email(email: str, session: AsyncSession) -> None:
    user = await get_user_by_email(email, session)
    user.confirmed = True
    await session.commit()


async def save_reset_token(user: User, reset_token: str, session: AsyncSession) -> None:
    """
    Зберігає токен скидання пароля користувача.

    Parameters:
        user (User): Об'єкт користувача.
        reset_token (str): Токен скидання пароля.
        session (AsyncSession): Об'єкт сесії бази даних.

    """
    user.reset_token = reset_token
    await session.commit()


async def get_user_by_reset_token(
    reset_token: str, session: AsyncSession
) -> User | None:
    """
    Отримує об'єкт користувача за токеном скидання пароля.

    Parameters:
        reset_token (str): Токен скидання пароля.
        session (AsyncSession): Об'єкт сесії бази даних.

    Returns:
        User: Об'єкт користувача, якщо знайдено, або None, якщо не знайдено.

    """
    try:
        result = await session.execute(
            select(User).filter(User.reset_token == reset_token)
        )
        user = result.scalar_one_or_none()
        return user
    except NoResultFound:
        return None


async def update_avatar(email, url: str, session: AsyncSession) -> User:
    user = await get_user_by_email(email, session)
    user.avatar = url
    await session.commit()
    return user
