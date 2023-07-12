import secrets
from fastapi import APIRouter,\
                    HTTPException,\
                    Depends,\
                    Response,\
                    status,\
                    Security,\
                    BackgroundTasks,\
                    Request,\
                    UploadFile,\
                    File


from fastapi.security import OAuth2PasswordRequestForm,\
                             HTTPAuthorizationCredentials,\
                             HTTPBearer

from pydantic import EmailStr

from sqlalchemy.ext.asyncio import AsyncSession

from database.connect import get_session
from database.models import User
from schemas import LoginResponse, RequestEmail, UserDb, UserModel, UserResponse

from repository import users as repository_users
from services.auth import auth_service
from services.email import send_email, reset_password_by_email

import cloudinary
import cloudinary.uploader

from conf.config import settings



router = APIRouter(tags=["User"])
security = HTTPBearer()


@router.post("/signup", response_model=UserResponse, 
             status_code=status.HTTP_201_CREATED)
async def signup(body: UserModel, 
                 background_tasks: BackgroundTasks, 
                 request: Request,
                 session: AsyncSession = Depends(get_session)):
    """
    Створює нового користувача.

    Параметри:
    - body (UserModel): Модель користувача, що містить дані для створення користувача.
    - background_tasks (BackgroundTasks): Об'єкт для виконання фонових задач асинхронно.
    - request (Request): Об'єкт запиту FastAPI.
    - session (AsyncSession): Об'єкт сесії бази даних.

    Повертає:
    - UserResponse: Об'єкт відповіді, який містить створеного користувача та
      повідомлення про успішне створення.

    Викликає:
    - HTTPException: Якщо обліковий запис вже існує.
    """

    exist_user = await repository_users.get_user_by_email(body.email, session)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Account already exists")
    body.password = auth_service.get_password_hash(body.password)
    new_user = await repository_users.create_user(body, session)
    background_tasks.add_task(send_email, 
                              new_user.email, 
                              new_user.username, 
                              request.base_url)
    return {"user": new_user, 
            "detail": "User successfully created. Check your email for confirmation."}


@router.post("/login", response_model=LoginResponse)
async def login(body: OAuth2PasswordRequestForm = Depends(),  
                session: AsyncSession = Depends(get_session)):
    """
    # Аутентифікація користувача та отримання токенів доступу.

    ## Параметри:
    - body (OAuth2PasswordRequestForm): Форма запиту аутентифікації, яка
      містить дані електронної пошти та пароля.
    - session (SAsyncSession): Об'єкт сесії бази даних.

    ## Повертає:
    - dict: Об'єкт, що містить користувача та токен доступу.

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
    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Email not confirmed")
    # Generate JWT
    access_token = await auth_service.create_access_token(data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await repository_users.update_token(user, refresh_token, session)

    return LoginResponse(user={
                            "username": user.username, 
                            "email": user.email,
                            "avatar": user.avatar},
                        access_token=access_token,
                        refresh_token=refresh_token)


@router.get('/refresh_token', response_model=LoginResponse, include_in_schema=False)
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Security(security), 
    session: AsyncSession = Depends(get_session)):
    """
    # Оновлює токен доступу за допомогою токена оновлення.

    ## Параметри:
    - credentials (HTTPAuthorizationCredentials): Об'єкт, що містить
    відправлені HTTP-заголовки авторизації.
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
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid refresh token")

    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token = await auth_service.create_refresh_token(
        data={"sub": email})
    await repository_users.update_token(user, refresh_token, session)
    return LoginResponse(user={
                            "username": user.username,
                            "email": user.email
                            },
                        access_token=access_token)

@router.get("/current", response_model=UserDb)
async def read_users_me(
    current_user: User = Depends(auth_service.get_current_user)
    ):

    return current_user


@router.get("/logout")
async def logout(response: Response, 
                 current_user: User = Depends(auth_service.get_current_user),
                 session: AsyncSession = Depends(get_session)
                 ):
    """
    # Вихід користувача з видаленням токена доступу та закриття сесії бази даних.

    ## Параметри:

    - `response` (Response): Об'єкт відповіді HTTP.
    - `current_user` (User): Поточний користувач, отриманий залежностями.
    - `session` (AsyncSession): Об'єкт сесії бази даних.

    ## Повертає:

    - Словник з повідомленням про вихід з системи: `{"message": "Logged out: {username}"}`.

    """

    # Видалення токена із заголовка запиту
    response.headers["Authorization"] = ""

    # Закрытие сессии базы данных
    await session.close()

    return {"message": f"Logged out: {current_user.username}"}


@router.get('/confirmed_email/{token}')
async def confirmed_email(token: str, 
                          session: AsyncSession = Depends(get_session)):
    """
    # Підтвердження електронної пошти за допомогою токена.

    ## Параметри:

    - `token` (str): Токен підтвердження електронної пошти.
    - `session` (AsyncSession): Об'єкт сесії бази даних.

    ## Повертає:

    - Словник з повідомленням про підтвердження електронної пошти: `{"message": "Email confirmed"}`.

    **Виключення:**

    - `HTTPException`: Якщо сталася помилка під час підтвердження електронної пошти.

    """

    email = await auth_service.get_email_from_token(token)
    user = await repository_users.get_user_by_email(email, session)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Verification error")
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    await repository_users.confirmed_email(email, session)
    return {"message": "Email confirmed"}


@router.post('/request_email')
async def request_email(body: RequestEmail, 
                        background_tasks: BackgroundTasks, 
                        request: Request,
                        session: AsyncSession = Depends(get_session)):
    
    """
    # Надсилає запит на підтвердження електронної пошти.

    ## Параметри:

    - `body` (RequestEmail): Об'єкт, що містить дані запиту електронної пошти.
    - `background_tasks` (BackgroundTasks): Об'єкт фонових задач FastAPI.
    - `request` (Request): Об'єкт запиту HTTP.
    - `session` (AsyncSession): Об'єкт сесії бази даних.

    ## Повертає:

    - Словник з повідомленням про надіслання запиту на підтвердження електронної пошти: `{"message": "Check your email for confirmation."}`.

    """

    user = await repository_users.get_user_by_email(body.email, session)

    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    if user:
        background_tasks.add_task(send_email, user.email, user.username, request.base_url)
    return {"message": "Check your email for confirmation."}


@router.post("/forgot-password")
async def forgot_password(
    email: EmailStr, 
    background_tasks: BackgroundTasks,
    request: Request,  
    session: AsyncSession = Depends(get_session)
):
    user = await repository_users.get_user_by_email(email, session)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User not found")

    # Генеруємо токен скидання паролю
    reset_token = secrets.token_hex(16)

    # Зберігаємо токен скидання паролю у базу даних для подальшої перевірки 
    await repository_users.save_reset_token(user, reset_token, session)

    background_tasks.add_task(reset_password_by_email, 
                              email, 
                              user.username,
                              reset_token,
                              request.base_url)

    return {"message": "Password reset initiated"}

@router.post("/reset-password")
async def reset_password(
    reset_token: str, 
    new_password: str,
    session: AsyncSession = Depends(get_session)
    ):
    """
    # Ініціює скидання пароля для користувача за допомогою електронної пошти.

    ## Параметри:

    - `email` (EmailStr): Електронна пошта користувача.
    - `background_tasks` (BackgroundTasks): Об'єкт фонових задач FastAPI.
    - `request` (Request): Об'єкт запиту HTTP.
    - `session` (AsyncSession): Об'єкт сесії бази даних.

    ## Повертає:

    - Словник з повідомленням про ініціювання скидання пароля: 
    `{"message": "Password reset initiated"}`.

    ## Виключення:

    - `HTTPException`: Якщо користувач не знайдений у базі даних.

    """

    user = await repository_users.get_user_by_reset_token(reset_token, session)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Invalid reset token")

    # Оновлюємо пароль користувача
    user.password = auth_service.get_password_hash(new_password)
    user.reset_token = None

    await session.commit()

    return {"message": "Password reset successfully"}


@router.patch('/avatar', response_model=UserDb)
async def update_avatar_user(file: UploadFile = File(), 
                             current_user: User = Depends(auth_service.get_current_user),
                             session: AsyncSession = Depends(get_session)):
    """
    # Додає/Оновлює аватар користувача за допомогою завантаженого файлу.

    ## Параметри:

    - `file` (UploadFile): Об'єкт завантаженого файлу з аватаром.
    - `current_user` (User): Поточний користувач, отриманий залежностями.
    - `session` (AsyncSession): Об'єкт сесії бази даних.

    ## Повертає:

    - Об'єкт 

    ```json
    {
        "id": 1,
        "username": "sergiokapone",
        "email": "user@example.com",
        "created_at": "2023-07-11T10:30:00.000Z",
        "avatar": "https://example.com/avatar.jpg"
    }
    
    ```
    з оновленими даними користувача.

    """

    cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True
    )

    r = cloudinary.uploader.upload(file.file, 
                                   public_id=f'ContactsApp/{current_user.username}', 
                                   overwrite=True)
    src_url = cloudinary.CloudinaryImage(
        f'ContactsApp/{current_user.username}').build_url(
                                   width=250, 
                                   height=250, 
                                   crop='fill', 
                                   version=r.get('version'))
    user = await repository_users.update_avatar(
                                   current_user.email, 
                                   src_url, 
                                   session)
    return user