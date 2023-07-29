"""
Run Uvicorn server with your ASGI application.

This script starts the Uvicorn server with your ASGI application, allowing you to serve the application on a specified
host and port.

Usage::
- Ensure the required modules are installed by running ``pipenv install uvicorn``.



Example::

    To start the server with the default settings, run::
    
        python src/main.py
"""

import uvicorn

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from fastapi_limiter.depends import RateLimiter
from fastapi_limiter import FastAPILimiter
import redis.asyncio as redis



from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from conf import settings


from database.connect import get_session

from routes.auth_routs import router as auth_router
from routes.contacts_routs import router as contacts_router


app = FastAPI(
    title="Contacts Dadabase",
    description="API for Connecting with Contacts Dadabase",
     exclude=["Body_login_users_login_post", "TokenModel"]
    )

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_router, prefix='/users')
app.include_router(contacts_router, prefix='/contacts')

@app.on_event("startup")
async def startup():
    r = redis.from_url(settings.redis_host, encoding="utf-8", decode_responses=True)
    await  FastAPILimiter.init(r)


@app.get("/", tags=["Root"],
# dependencies=[Depends(RateLimiter(times=2, seconds=5))]
)
async def root():
    """
    # Кореневий маршрут

    Це головна точка вхідної точки API.

    ## Відповідь

    Якщо все пройшло успішно, за цією адресою видається вітальне слово
    - **message**: Привітальне повідомлення ("Hello World!")
    """
    return {"message": "Hello World!"}


@app.get("/api/healthchecker", tags=["Root"])
async def healthchecker(session: AsyncSession = Depends(get_session)):
    """
    # Health Checker

    Перевіряє стан з'єднання з базою даних.

    ## Параметри запиту
    - **session**: Асинхронна сесія бази даних (залежність)

    ## Відповідь
    - **message**: Повідомлення про успішне з'єднання з базою даних

    ## Помилки
    - **HTTP_500_INTERNAL_SERVER_ERROR**: Помилка підключення до бази даних або неправильна конфігурація бази даних
    """

    try:
        result = await session.execute(text("SELECT 1"))
        rows = result.fetchall()

        if not rows:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database is not configured correctly",
            )

        return {"message": "You successfully connected to the database!"}
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error connecting to the database",
        )