
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
                         access_token: str = Header(...,
                                description="Введіть токен доступу",
                                convert_underscores=False),
                         session: AsyncSession = Depends(get_session),
                         ):
    email = auth_service.extract_email_from_token(access_token)

    return await contacts.create_contact(contact, email, session)

@router.get("/")
async def get_all_contacts(
    access_token: str = Header(...,
                                description="Введіть токен доступу",
                                convert_underscores=False),
    session: AsyncSession = Depends(get_session),
                            ):
    
    email = auth_service.extract_email_from_token(access_token)

    return await contacts.get_all_contacts(session, email)

@router.delete("/{contact_id}")
async def delete_contact(contact_id: int,
                         access_token: str = Header(...,
                                description="Введіть токен доступу",
                                convert_underscores=False),
                      session: AsyncSession = Depends(get_session)):
    email = auth_service.extract_email_from_token(access_token)

    return await contacts.delete_contact(contact_id, email, session)


@router.put("/{contact_id}")
async def delete_contact(contact_id: int,
                         contact: ContactCreate,
                         access_token: str = Header(...,
                                description="Введіть токен доступу",
                                convert_underscores=False),
                      session: AsyncSession = Depends(get_session)):
    
    email = auth_service.extract_email_from_token(access_token)

    print("--------->", email)

    return await contacts.update_contact(contact_id, contact, email, session)