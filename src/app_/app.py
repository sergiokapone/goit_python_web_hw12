
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordBearer
from .users import get_current_user

from . import contacts_routes, auth_routs


from database.connect import get_session


app = FastAPI()


# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)



oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

app.include_router(contacts_routes.router)
app.include_router(auth_routs.router)


@app.get("/", tags=["Root"])
async def root():
    return {"message": "Hello World!"}


@app.get("/api/healthchecker", tags=["Root"])
async def healthchecker(session: AsyncSession = Depends(get_session)):
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