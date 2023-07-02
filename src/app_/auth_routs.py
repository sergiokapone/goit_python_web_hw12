from fastapi import status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends, HTTPException, Header

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.connect import get_session

from .schemas import UserModel, UserResponse, Token

from database.models import User
from .users import create_access_token, get_current_user, decode_token, get_user_by_id, generate_refresh_token, Hash



router = APIRouter(prefix="/users", tags=["User"])
hash_handler = Hash()

@router.post("/signup", 
             response_model=UserResponse, 
             status_code=status.HTTP_201_CREATED)
async def signup(user_create: UserModel, 
                 session: AsyncSession = Depends(get_session)):
    exist_user = await session.execute(select(User).filter(User.email == user_create.email))

    if exist_user.scalar_one_or_none() is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")

    refresh_token = generate_refresh_token() 

    new_user = User(email=user_create.email, 
                    password=hash_handler.get_password_hash(user_create.password), 
                    refresh_token=refresh_token)
    
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    access_token = await create_access_token({"id": new_user.id})

    return {"user": {"username": user_create.username, "email": user_create.email}, "token": access_token}



@router.post("/login", response_model=Token)
async def login(body: OAuth2PasswordRequestForm = Depends(), 
                session: AsyncSession = Depends(get_session)):
    user = session.execute(select(User).filter(User.email == body.username).first())

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                             detail="Invalid email")
    
    if not hash_handler.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                             detail="Invalid password")
    # Generate JWT
    access_token = await create_access_token(data={"sub": user.email})
    return Token(access_token=access_token, token_type="bearer")


@router.get("/current")
async def get_current_user(authorization: str = Header(...)):
    try:
        # Декодируем токен для получения информации о пользователе
        user_id = decode_token(authorization)
        # Получаем информацию о текущем пользователе
        current_user = get_user_by_id(user_id)
        return current_user
    except:
        # Если токен недействительный или отсутствует, возбуждаем исключение
        raise HTTPException(status_code=401, detail="Missing or invalid token")


@router.get("/")
async def root():
    return {"message": "Hello World"}


@router.get("/secret")
async def read_item(current_user: User = Depends(get_current_user)):
    return {"message": "secret router", "owner": current_user.email}