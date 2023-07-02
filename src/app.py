from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


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