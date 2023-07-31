from datetime import date, datetime

from fastapi import Depends, HTTPException
from fastapi import status

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from database import get_session
from database import Contact, User

from schemas import ContactCreate


async def create_contact(
    contact: ContactCreate, user: User, session: AsyncSession
):
    """
    Створити контакт.

    :param contact: Об'єкт, що містить дані для створення контакту.
    :type contact: ContactCreate
    :param user: Користувач, для якого створюється контакт.
    :type user: User
    :param session: Об'єкт сеансу бази даних (за замовчуванням отримується з `get_session`).
    :type session: AsyncSession
    :return: Новостворений об'єкт контакту.
    :rtype: Contact

    Створює новий контакт з наданими даними. Використовує електронну пошту
    користувача для зв'язку з власником контакту.
    """

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )

    try:
        new_contact = Contact(
            first_name=contact.first_name,
            last_name=contact.last_name,
            email=contact.email,
            phone_number=contact.phone_number,
            birthday=datetime.strptime(contact.birthday, "%Y-%m-%d").date(),
            additional_data=contact.additional_data,
            user=user,
        )
        session.add(new_contact)
        await session.flush()
        await session.refresh(new_contact)
        await session.commit()
        return new_contact
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Contact with the same email already exists",
        )


async def get_all_contacts(user: User, session: AsyncSession):
    """
    Отримати всі контакти.

    :param user: Об'єкт поточного користувача.
    :type user: User
    :param session: Об'єкт сеансу бази даних.
    :type session: AsyncSession
    :return: Список контактів.
    :rtype: List[Contact]

    Отримує всі контакти, які належать користувачу з вказаною електронною поштою.
    """

    results = await session.execute(select(Contact).filter(Contact.user_id == user.id))

    contacts = results.scalars().all()
    return contacts


async def delete_contact(
    contact_id: int, user: User, session: AsyncSession):
    """
    Видалити контакт.

    :param contact_id: Ідентифікатор контакту, який потрібно видалити.
    :type contact_id: int
    :param user: Об'єкт поточного користувача.
    :type user: User
    :param session: Об'єкт сеансу бази даних (за замовчуванням отримується з `get_session`).
    :type session: AsyncSession
    :return: Результат видалення контакту у вигляді словника з повідомленням та видаленим контактом.
    :rtype: dict

    Видаляє контакт з вказаним ідентифікатором, якщо користувач з вказаною
    електронною поштою є власником контакту.
    """

    contact = await session.get(Contact, contact_id)

    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    if contact.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )

    await session.delete(contact)
    await session.commit()
    return {"message": "Contact deleted", "contact": contact}


async def update_contact(
    contact_id: int,
    contact: ContactCreate,
    user: User,
    session: AsyncSession = Depends(get_session),
):
    """
    Оновити контакт.

    :param contact_id: Ідентифікатор контакту, який потрібно оновити.
    :type contact_id: int
    :param contact: Об'єкт, що містить нові дані для оновлення контакту.
    :type contact: ContactCreate
    :param user: Об'єкт поточного користувача.
    :type user: User
    :param session: Об'єкт сеансу бази даних (за замовчуванням отримується з `get_session`).
    :type session: AsyncSession
    :return: Оновлений об'єкт контакту.
    :rtype: Contact

    Оновлює контакт з вказаним ідентифікатором, якщо користувач з вказаною
    електр
    """

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )

    existing_contact = await session.get(Contact, contact_id)

    if not existing_contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    if existing_contact.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )

    try:
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
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Contact with the same email already exists",
        )

    return existing_contact


def is_upcoming_birthday(birthday: date, start_date: date, end_date: date) -> bool:
    """
    Визначити, чи наступає день народження.

    :param birthday: Дата дня народження.
    :type birthday: date
    :param start_date: Початкова дата для визначення наступаючих днів народження.
    :type start_date: date
    :param end_date: Кінцева дата для визначення наступаючих днів народження.
    :type end_date: date
    :return: `True`, якщо день народження наступає, інакше `False`.
    :rtype: bool
    """

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
    days: int,
    user: User,
    session: AsyncSession
):
    """
    Отримати наближені дні народження контактів.

    :param days: Кількість днів для визначення наближених днів народження.
    :type days: int
    :param user: Об'єкт користувача.
    :type user: User
    :param session: Об'єкт сесії бази даних (за замовчуванням отримується з `get_session`).
    :type session: AsyncSession, optional
    :return: Список результатів запиту до бази даних.
    :rtype: List[dict]

    Визначає наближені дні народження контактів для заданого користувача.
    Результати запиту повертаються у вигляді списку словників з контактами,
    у яких дні народження наступають протягом вказаної кількості днів.

    Викидає:
    - HTTPException: Якщо користувач не автентифікований.
    """

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )

    today = datetime.now().date()

    upcoming_birthdays = []
    results = await session.execute(select(Contact).filter(Contact.user_id == user.id))
    contacts = results.scalars().all()

    for contact in contacts:
        birthday = contact.birthday
        next_birthday = datetime(today.year, birthday.month, birthday.day).date()

        if next_birthday < today:
            next_birthday = datetime(
                today.year + 1, birthday.month, birthday.day
            ).date()

        days_until_birthday = (next_birthday - today).days
        if days_until_birthday <= days:
            upcoming_birthdays.append(contact)

    return upcoming_birthdays
