
from sqlalchemy.ext.asyncio import AsyncSession
from repository.users import get_user_by_email
from database.connect import get_session

from fastapi import APIRouter, Depends, Header

from schemas import ContactCreate
from database.models import User

from repository import contacts
from services.auth import auth_service

router = APIRouter(tags=["Contacts"])

@router.post("/")
async def create_contact(contact: ContactCreate, 
                         session: AsyncSession = Depends(get_session),
                         current_user: User = Depends(get_user_by_email)):
    return await contacts.create_contact(contact, session, current_user)

@router.get("/")
async def get_all_contacts(
    access_token: str = Header(...,
                                description="Введіть токен доступу",
                                convert_underscores=False),
    session: AsyncSession = Depends(get_session),
                            ):
    
    email = auth_service.extract_email_from_token(access_token)

    return await contacts.get_all_contacts(session, email)

@router.get("/{contact_id}")
async def get_contact(contact_id: int,
                      session: AsyncSession = Depends(get_session)):
    return await contacts.get_contact(contact_id, session)
