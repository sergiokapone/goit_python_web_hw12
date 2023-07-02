from typing import Optional
from passlib.context import CryptContext

from jose import JWTError, jwt

from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer

from sqlalchemy.ext.asyncio import AsyncSession

from datetime import datetime, timedelta

from database.connect import get_session
from repository import users as repository_users


class Auth:
    """
    Клас, що надає функціонал автентифікації та генерації токенів.

    Attributes:
        pwd_context (CryptContext): Контекст шифрування паролей.
        SECRET_KEY (str): Секретний ключ для підпису токенів.
        ALGORITHM (str): Алгоритм шифрування для підпису токенів.
        oauth2_scheme (OAuth2PasswordBearer): Залежність для отримання токену з HTTP запиту.

    Methods:
        verify_password(plain_password, hashed_password): Перевіряє валідність паролю.
        get_password_hash(password): Генерує хеш паролю.
        create_access_token(data, expires_delta): Генерує новий токен доступу.
        create_refresh_token(data, expires_delta): Генерує новий оновлювальний токен.
        decode_refresh_token(refresh_token): Розшифровує оновлювальний токен.
        get_current_user(token, db): Отримує поточного користувача на основі переданого токену.
    """

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    SECRET_KEY = "secret_key"
    ALGORITHM = "HS256"
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

    def verify_password(self, plain_password, hashed_password):
        """
        Перевіряє валідність паролю.

        Args:
            plain_password (str): Пароль у відкритому вигляді.
            hashed_password (str): Хеш паролю.

        Returns:
            bool: True, якщо пароль валідний, False - в іншому випадку.
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        """
        Генерує хеш паролю.

        Args:
            password (str): Пароль у відкритому вигляді.

        Returns:
            str: Хеш паролю.
        """
        return self.pwd_context.hash(password)

    async def create_access_token(self, data: dict, 
                                  expires_delta: Optional[float] = None):
        """
        Генерує новий токен доступу.

        Args:
            data (dict): Дані, які будуть закодовані у токені.
            expires_delta (float, optional): Термін дії токену у секундах. За замовчуванням - 15 хвилин.

        Returns:
            str: Згенерований токен доступу.
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "access_token"})
        encoded_access_token = jwt.encode(to_encode, 
                                          self.SECRET_KEY, 
                                          algorithm=self.ALGORITHM)
        return encoded_access_token

    async def create_refresh_token(self, data: dict, 
                                   expires_delta: Optional[float] = None):
        """
        Генерує новий оновлювальний токен.

        Args:
            data (dict): Дані, які будуть закодовані у токені.
            expires_delta (float, optional): Термін дії токену у секундах. За замовчуванням - 7 днів.

        Returns:
            str: Згенерований оновлювальний токен.
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update(
                          {
                            "iat": datetime.utcnow(), 
                            "exp": expire, 
                            "scope": "refresh_token"
                          }
                          )
        encoded_refresh_token = jwt.encode(to_encode, 
                                           self.SECRET_KEY, 
                                           algorithm=self.ALGORITHM)
        return encoded_refresh_token

    async def decode_refresh_token(self, refresh_token: str):
        """
        Розшифровує оновлювальний токен.

        Args:
            refresh_token (str): Оновлювальний токен.

        Returns:
            str: Електронна пошта, пов'язана з оновлювальним токеном.

        Raises:
            HTTPException: Виникає, якщо токен недійсний або містить неприпустимий обсяг дій.
        """
        try:
            payload = jwt.decode(refresh_token, 
                                 self.SECRET_KEY, 
                                 algorithms=[self.ALGORITHM])
            if payload['scope'] == 'refresh_token':
                email = payload['sub']
                return email
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                 detail='Invalid scope for token')
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='Could not validate credentials')

    async def get_current_user(self, token: str = Depends(oauth2_scheme),
                               session: AsyncSession = Depends(get_session)):
        """
        Отримує поточного користувача на основі переданого токену.

        Args:
            token (str, optional): Токен доступу. За замовчуванням використовується залежність "oauth2_scheme".
            session (AsyncSession, optional): Об'єкт сесії бази даних.

        Returns:
            User: Об'єкт поточного користувача.

        Raises:
            HTTPException: Виникає, якщо токен недійсний або не містить ідентифікатора користувача.
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            # Decode JWT
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'access_token':
                email = payload["sub"]
                if email is None:
                    raise credentials_exception
            else:
                raise credentials_exception
        except JWTError:
            raise credentials_exception

        user = await repository_users.get_user_by_email(email, session)
        if user is None:
            raise credentials_exception
        return user
    
    def extract_email_from_token(self, token):
        try:
            decoded_token = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            email = decoded_token.get("sub")
            return email
        except JWTError:
            return None

auth_service = Auth()
