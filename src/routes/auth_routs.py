from fastapi import APIRouter, HTTPException, Depends, Header, status, Security
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer

from sqlalchemy.ext.asyncio import AsyncSession

from database.connect import get_session
from schemas import UserModel, UserResponse, TokenModel

from repository import users as repository_users
from services.auth import auth_service

router = APIRouter(tags=["User"])
security = HTTPBearer()


@router.post("/signup", response_model=UserResponse, 
             status_code=status.HTTP_201_CREATED)
async def signup(body: UserModel, session: AsyncSession = Depends(get_session)):
    """
    # Створює нового користувача.

    ## Параметри:
    - body (UserModel): Модель користувача, що містить дані для створення користувача.
    - session (AsyncSession): Об'єкт сесії бази даних.

    ## Повертає:
    - UserResponse: Об'єкт відповіді, який містить створеного користувача та повідомлення про успішне створення.

    ## Raises:
    - HTTPException: Якщо обліковий запис вже існує.

    """
    exist_user = await repository_users.get_user_by_email(body.email, session)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Account already exists")
    body.password = auth_service.get_password_hash(body.password)
    new_user = await repository_users.create_user(body, session)
    return {"user": new_user, "detail": "User successfully created"}


@router.post("/login")
async def login(body: OAuth2PasswordRequestForm = Depends(),  
                session: AsyncSession = Depends(get_session)):
    """
    # Аутентифікація користувача та отримання токенів доступу.

    ## Параметри:
    - body (OAuth2PasswordRequestForm): Форма запиту аутентифікації, яка містить дані електронної пошти та пароля.
    - session (SAsyncSession): Об'єкт сесії бази даних.

    ## Повертає:
    - TokenModel: Модель токена, яка містить токен доступу та оновлення.

    ## Raises:
    - HTTPException: Якщо недійсна електронна пошта або пароль.

    """

    user = await repository_users.get_user_by_email(body.username, session)
    print(body.password, user.password)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid email")
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid password")
    # Generate JWT
    access_token = await auth_service.create_access_token(data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await repository_users.update_token(user, refresh_token, session)
    return {
            "user": {
                "username": "angelka",
                "email": user.email
            },
            "token": access_token
            }


@router.get('/refresh_token', response_model=TokenModel, include_in_schema=False)
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Security(security), 
    session: AsyncSession = Depends(get_session)):
    """
    # Оновлює токен доступу за допомогою токена оновлення.

    ## Параметри:
    - credentials (HTTPAuthorizationCredentials): Об'єкт, що містить відправлені HTTP-заголовки авторизації.
    - session (AsyncSession): Об'єкт сесії бази даних.

    ## Повертає:
    - TokenModel: Модель токена, яка містить новий токен доступу та оновлення.

    ## Raises:
    - HTTPException: Якщо недійсний токен оновлення або помилка під час декодування.

    """
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repository_users.get_user_by_email(email, session)
    if user.refresh_token != token:
        await repository_users.update_token(user, None, session)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": email})
    await repository_users.update_token(user, refresh_token, session)
    return {
            "user": {
                "username": "angelka",
                "email": email
            },
            "token": access_token
            }



@router.get("/current")
async def get_current_user(access_token: str = Header(...,
                                description="Введіть токен доступу",
                                convert_underscores=False),
                                session: AsyncSession = Depends(get_session)
                                ):
    """
    # Отримати поточного користувача.

    Отримує поточного користувача за допомогою токена доступу і об'єкта сеансу, повертає ім'я користувача та електронну пошту.

    ## Параметри:
    - access_token (str): Токен доступу користувача.
    - session (AsyncSession): Об'єкт сеансу для з'єднання з базою даних.

    ## Повертає:
    - dict: Результат з поточним користувачем у вигляді словника з ім'ям користувача та електронною поштою.
    """

    current_user = await auth_service.get_current_user(access_token, session)

    return {"username": current_user.username, 
            "email": current_user.email
            }

@router.post("/logout")
async def logout_user(access_token: str = Header(...,
                                description="Введіть токен доступу",
                                convert_underscores=False),
                      session: AsyncSession = Depends(get_session)):
    
    session.close()

    return {"message": "User logged out successfully"}