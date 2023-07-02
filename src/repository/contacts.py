from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from repository import users as repository_users
from database.connect import get_session

from fastapi import Depends, HTTPException
from fastapi import status

from schemas import ContactCreate
from database.models import Contact

async def create_contact(
                contact: ContactCreate, 
                email: str = None,
                session: AsyncSession = Depends(get_session)
                        ):
    
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


async def get_all_contacts(
        email: str = None,
        session: AsyncSession = Depends(get_session)
        ):
    
    current_user = await repository_users.get_user_by_email(email, session)

    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Not authenticated")
    
    result = await session.execute(select(Contact).filter(Contact.user_id == current_user.id))
    contacts = result.all()
    return contacts

async def delete_contact(contact_id: int,
                         email: str = None, 
                         session: AsyncSession = Depends(get_session)):
    
    current_user = await repository_users.get_user_by_email(email, session)



    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Not authenticated")

    contact = await session.get(Contact, contact_id)

    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    

    contact = await session.get(Contact, contact_id)
    
    if contact.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    await session.delete(contact)
    await session.commit()
    return {"message": "Contact deleted", "contact": contact}


async def update_contact(contact_id: int,
                         contact: ContactCreate,
                         email: str = None, 
                         session: AsyncSession = Depends(get_session)):
    
    current_user = await repository_users.get_user_by_email(email, session)

    print("--------->", current_user)
    
    existing_contact = await session.get(Contact, contact_id)

    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Not authenticated")


    if not existing_contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
   
    if  existing_contact.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    

    existing_contact.first_name = contact.first_name
    existing_contact.last_name = contact.last_name
    existing_contact.email = contact.email
    existing_contact.phone_number = contact.phone_number
    existing_contact.birthday = datetime.strptime(
        contact.birthday, "%Y-%m-%d"
    ).date()
    existing_contact.additional_data = contact.additional_data

    await session.commit()
    await session.refresh(existing_contact)
    return existing_contact