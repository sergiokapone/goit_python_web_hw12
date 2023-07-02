from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from repository import users as repository_users
from database.connect import get_session

from fastapi import Depends, HTTPException
from fastapi import status

from schemas import ContactCreate
from database.models import Contact

async def create_contact(contact: ContactCreate, 
                        session: AsyncSession = Depends(get_session), 
                        email: str = None):
    
    current_user = await repository_users.get_user_by_email(email, session)

    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    new_contact = Contact(
        first_name=contact.first_name,
        last_name=contact.last_name,
        email=contact.email,
        phone_number=contact.phone_number,
        birthday=datetime.strptime(contact.birthday, "%Y-%m-%d").date(),
        additional_data=contact.additional_data,
        user_id=current_user.id
    )
    session.add(new_contact)
    await session.flush()
    await session.refresh(new_contact)
    await session.commit()
    return new_contact


async def get_all_contacts(session: AsyncSession = Depends(get_session),
                        email: str = None):
    
    current_user = await repository_users.get_user_by_email(email, session)

    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Not authenticated")

    result = await session.execute(select(Contact).filter(Contact.user_id == current_user.id))
    contacts = result.all()
    return contacts


async def get_contact(contact_id: int, 
                      session: AsyncSession = Depends(get_session)):
    contact = await session.execute(select(Contact).filter(Contact.id == contact_id))
    result = contact.scalar_one_or_none()
    if result is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return result
