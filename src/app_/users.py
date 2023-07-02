import secrets

from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException
from fastapi import status
from fastapi.security import OAuth2PasswordBearer

from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext

from jose import jwt

from database.models import User
from database.connect import get_session



class Hash:
    """
    Клас, який надає функціональність для перевірки паролів і генерації хеш-значень паролів.

    Attributes:
        pwd_context (CryptContext): Об'єкт CryptContext для обробки паролів.

    Methods:
        verify_password(plain_password, hashed_password):
            Перевіряє, чи співпадає незахешований пароль з хеш-значенням пароля.
            
        get_password_hash(password):
            Повертає хеш-значення незахешованого пароля.

    """

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(self, plain_password, hashed_password):
        """
        Перевіряє, чи співпадає незахешований пароль з хеш-значенням пароля.

        Args:
            plain_password (str): Незахешований пароль.
            hashed_password (str): Хеш-значення пароля.

        Returns:
            bool: True, якщо пароль співпадає з хеш-значенням, False - інакше.
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        """
        Повертає хеш-значення незахешованого пароля.

        Args:
            password (str): Незахешований пароль.

        Returns:
            str: Хеш-значення пароля.
        """
        return self.pwd_context.hash(password)


SECRET_KEY = "secret_key"
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


async def create_access_token(data: dict, 
                              expires_delta: Optional[float] = None
                              ):
    """
    Функція для створення доступного токену.

    Функція використовується для створення JWT (JSON Web Token) токену, який містить передані дані. Якщо вказано expires_delta, то до часу створення токену додається відповідний інтервал. Токен закодовується з використанням секретного ключа SECRET_KEY та алгоритму ALGORITHM. Повертається закодований JWT токен.

    Args:
        data (dict): Словник з даними, які будуть включені в токен.
        expires_delta (Optional[float]): Опціональний параметр, що визначає час життя токену в секундах.

    Returns:
        str: Закодований JWT токен.
    """  # noqa: E501

    jwt_payload = data.copy()
    """
    Сюди передасться словник вигдяду
    {
        "name": Ім'я користувача,
        "email": Email користувача,
        "password" ?
    }
    """
    

    if expires_delta:
        expire = datetime.utcnow() + timedelta(seconds=expires_delta)
    else:
        expire = datetime.utcnow() + timedelta(minutes=60)

    jwt_payload.update({"exp": expire})
    encoded_jwt = jwt.encode(jwt_payload, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def decode_token(token: str) -> dict:
    """
    Функція для розшифрування JWT токену.

    Args:
        token (str): Закодований JWT токен.

    Returns:
        dict: Розкодовані дані токену у вигляді словника.

    Raises:
        jwt.ExpiredSignatureError: Виникає, якщо токен має закінчений термін дії.
        jwt.InvalidTokenError: Виникає, якщо токен є недійсним.
    """
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return decoded_token
    except jwt.ExpiredSignatureError:
        # Обробка закінченого терміну дії токену
        raise jwt.ExpiredSignatureError("Token has expired")
    except jwt.InvalidTokenError:
        # Обробка недійсного токену
        raise jwt.InvalidTokenError("Invalid token")

    
def generate_refresh_token() -> str:
    """
    Генерує оновлювальний токен.

    Returns:
        str: Згенерований оновлювальний токен.
    """
    refresh_token = secrets.token_urlsafe(32)
    return refresh_token


async def get_user_by_id(
    user_id: int,
    session: AsyncSession = Depends(get_session),
) -> Optional[User]:
    """
    Отримує користувача за його ідентифікатором.

    Args:
        user_id (int): Ідентифікатор користувача.
        session (AsyncSession, optional): Асинхронний об'єкт сесії бази даних. За замовчуванням використовується залежність "get_session".

    Returns:
        Optional[User]: Об'єкт користувача, якщо знайдено, або None, якщо користувач не знайдений.
    """  # noqa: E501

    user = await session.get(User, user_id)
    return user


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    Отримує поточного користувача на основі переданого JWT токену.

    Args:
        token (str, optional): JWT токен. За замовчуванням використовується залежність "oauth2_scheme".

    Returns:
        User: Об'єкт поточного користувача.

    Raises:
        HTTPException: Виникає, якщо токен є недійсним або не містить ідентифікатора користувача.
    """

    try:
        payload = decode_token(token)
        user_id: int = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                 detail="Invalid token")
        return await get_user_by_id(user_id)
    except jwt.JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                             detail="Invalid token")
