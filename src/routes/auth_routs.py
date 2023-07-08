from fastapi import APIRouter, HTTPException, Depends, Response, status, Security, BackgroundTasks, Request


from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer

from sqlalchemy.ext.asyncio import AsyncSession

from database.connect import get_session
from database.models import User
from schemas import CucrrentUserResponse, LoginResponse, RequestEmail, UserModel, UserResponse

from repository import users as repository_users
from services.auth import auth_service
from services.email import send_email

router = APIRouter(tags=["User"])
security = HTTPBearer()


@router.post("/signup", response_model=UserResponse, 
             status_code=status.HTTP_201_CREATED)
async def signup(body: UserModel, 
                 background_tasks: BackgroundTasks, 
                 request: Request,
                 session: AsyncSession = Depends(get_session)):
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
    - body (OAuth2PasswordRequestForm): Форма запиту аутентифікації, яка містить дані електронної пошти та пароля.
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

    return LoginResponse(user={"username": user.username, 
                        "email": user.email},
                        access_token=access_token,
                        refresh_token=refresh_token)


@router.get('/refresh_token', response_model=LoginResponse, include_in_schema=False)
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
    return LoginResponse(user={"username": user.username, "email": user.email},
                    access_token=access_token)

@router.get("/current", response_model=CucrrentUserResponse)
async def get_current_user(
    current_user: User = Depends(auth_service.get_current_user)
):
    """
    # Отримати поточного користувача.

    Отримує поточного користувача за допомогою токена доступу і об'єкта сеансу, повертає ім'я користувача та електронну пошту.

    ## Параметри:
    - current_user (User): Об'єкт поточного користувача.

    ## Повертає:
    - dict: Результат з поточним користувачем у вигляді словника з ім'ям користувача та електронною поштою.
    """

    return CucrrentUserResponse(
        username=current_user.username,
        email=current_user.email)




@router.get("/logout")
async def logout(response: Response, 
                 current_user: User = Depends(auth_service.get_current_user),
                 session: AsyncSession = Depends(get_session)
                 ):

    # Видалення токена із заголовка запиту
    response.headers["Authorization"] = ""

    # Закрытие сессии базы данных
    await session.close()

    return {"message": f"Logged out: {current_user.username}"}


@router.get('/confirmed_email/{token}')
async def confirmed_email(token: str, 
                          session: AsyncSession = Depends(get_session)):
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
    user = await repository_users.get_user_by_email(body.email, session)

    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    if user:
        background_tasks.add_task(send_email, user.email, user.username, request.base_url)
    return {"message": "Check your email for confirmation."}