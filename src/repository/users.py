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


from database.connect import get_session
from database.models import User

from services.auth import auth_service

from schemas import UserModel

async def get_user_by_email(email: str, 
                            session: AsyncSession = Depends(get_session)) -> User | None:
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


async def create_user(body: UserModel, 
                      session: AsyncSession = Depends(get_session)) -> User:
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

    new_user = User(username=body.username,
                    email=body.email,
                    password=body.password,
                    created_at=datetime.now(),
                    avatar=avatar,
                    refresh_token=refresh_token)

    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    return new_user


async def update_token(user: User, token: str | None, 
                    session: AsyncSession = Depends(get_session)) -> None:
    """
    Оновлює токен оновлення для користувача.

    Parameters:
        user (User): Об'єкт користувача.
        token (str | None): Токен оновлення або None, якщо токен не вказаний.
        session (AsyncSession): Об'єкт сесії бази даних.

    """
    user.refresh_token = token
    await session.commit()


async def confirmed_email(email: str, 
                          session: AsyncSession = Depends(get_session)) -> None:
    user = await get_user_by_email(email, session)
    print(user)
    user.confirmed = True
    await session.commit()