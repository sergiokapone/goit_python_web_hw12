from datetime import date, datetime, timedelta

from fastapi import Depends, HTTPException
from fastapi import status

from sqlalchemy import extract, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.connect import get_session
from database.models import Contact, User


from schemas import ContactCreate

async def create_contact(
                contact: ContactCreate, 
                user: User,
                session: AsyncSession = Depends(get_session)
                        ):
    
    """
    Створити контакт.

    Параметри:
    - contact (ContactCreate): Об'єкт, що містить дані для створення контакту.
    - email (str, optional): Електронна пошта користувача.
    - session (AsyncSession): Об'єкт сеансу для з'єднання з базою даних.

    Повертає:
    - Contact: Новостворений об'єкт контакту.

    Створює новий контакт з наданими даними. Використовує електронну пошту користувача для зв'язку з власником контакту.
    """
        

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    new_contact = Contact(
        first_name=contact.first_name,
        last_name=contact.last_name,
        email=contact.email,
        phone_number=contact.phone_number,
        birthday=datetime.strptime(contact.birthday, "%Y-%m-%d").date(),
        additional_data=contact.additional_data,
        user=user
    )
    session.add(new_contact)
    await session.flush()
    await session.refresh(new_contact)
    await session.commit()
    return new_contact


async def get_all_contacts(
    user: User,
    session: AsyncSession
):
    """
    Отримати всі контакти.

    Отримує всі контакти, які належать користувачу з вказаною електронною поштою.

    Параметри:
    - current_user (User): Об'єкт поточного користувача.
    - session (AsyncSession): Об'єкт сеансу для з'єднання з базою даних.

    Повертає:
    - List[Contact]: Список контактів.
    """
    result = await session.execute(
         select(Contact).filter(
         Contact.user_id == user.id)
         )
    contacts = result.all()
    return contacts


async def delete_contact(
    contact_id: int,
    user: User,
    session: AsyncSession = Depends(get_session)
):
    """
    # Видалити контакт.

    Видаляє контакт з вказаним ідентифікатором, якщо користувач з вказаною електронною поштою є власником контакту.

    Параметри:
    - contact_id (int): Ідентифікатор контакту, який потрібно видалити.
    - current_user (User): Об'єкт поточного користувача.
    - session (AsyncSession): Об'єкт сеансу для з'єднання з базою даних.

    Повертає:
    - dict: Результат видалення контакту у вигляді словника з повідомленням та видаленим контактом.
    """

    contact = await session.get(Contact, contact_id)

    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    if contact.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    await session.delete(contact)
    await session.commit()
    return {"message": "Contact deleted", "contact": contact}



async def update_contact(contact_id: int,
                         contact: ContactCreate,
                         user: User, 
                         session: AsyncSession = Depends(get_session)):
    """
    # Оновити контакт.

    Оновлює контакт з вказаним ідентифікатором, якщо користувач з вказаною електронною поштою є власником контакту.

    ## Параметри:
    - contact_id (int): Ідентифікатор контакту, який потрібно оновити.
    - contact (ContactCreate): Об'єкт, що містить нові дані для оновлення контакту.
    - email (str, optional): Електронна пошта користувача.
    - session (AsyncSession): Об'єкт сеансу для з'єднання з базою даних.

    ## Повертає:
    - Contact: Оновлений об'єкт контакту.

    """
        

        
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Not authenticated")
    

    existing_contact = await session.get(Contact, contact_id)

    if not existing_contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
   
    if existing_contact.user_id != user.id:
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


def is_upcoming_birthday(birthday: date, start_date: date, end_date: date) -> bool:
    birthday_this_year = start_date.replace(
        year=start_date.year, month=birthday.month, day=birthday.day
    )

    if start_date <= birthday_this_year <= end_date:
        return True

    birthday_next_year = birthday_this_year.replace(year=start_date.year + 1)

    if start_date <= birthday_next_year <= end_date:
        return True

    return False


async def get_upcoming_birthdays(
    days,
    user: User,
    session: AsyncSession = Depends(get_session),
):
    """
    Отримати наближені дні народження контактів.

    Параметри:
    - days (int): Кількість днів для визначення наближених днів народження.
    - email (int, опціонально): Електронна пошта користувача. Використовується для отримання поточного користувача.
    - session (AsyncSession, опціонально): Об'єкт сесії бази даних.

    Повертає:
    - результати (ResultProxy): Об'єкт, що містить результати запиту до бази даних.

    Викидає:
    - HTTPException: Якщо користувач не автентифікований.
    """


    
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Not authenticated")
    
    today = date.today()
    end_date = today + timedelta(days=days)
    results = await session.execute(
                select(Contact)
                .filter(
                    Contact.user_id == user.id,
                    extract('month', Contact.birthday) == today.month,
                    extract('day', Contact.birthday).between(today.day, end_date.day)
                )
                .order_by(Contact.birthday)
            )


    return [dict(row) for row in results]