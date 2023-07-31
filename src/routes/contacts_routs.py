from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import APIRouter, Depends, status

from database import get_session
from database import User

from schemas import ContactCreate

from repository import contacts
from services.auth import auth_service

router = APIRouter(tags=["Contacts"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_contact(
    contact: ContactCreate,
    current_user: User = Depends(auth_service.get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    # Створити контакт.

    Маршрут створює новий контакт з наданими даними за допомогою введеного токену доступу.

    ## Параметри:
    - contact (ContactCreate): Об'єкт, що містить дані для створення контакту.
    - access_token (str): Токен доступу для аутентифікації користувача.
    - session (AsyncSession): Об'єкт сеансу для з'єднання з базою даних.

    ## Повертає:
    - Contact: Новостворений об'єкт контакту.

    """

    return await contacts.create_contact(contact, current_user, session)


@router.get("/")
async def get_all_contacts(
    current_user: User = Depends(auth_service.get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    # Отримати всі контакти.

    Маршрут отримує всі контакти, які належать користувачу, за допомогою введеного токену доступу.

    ## Параметри:
    - access_token (str): Токен доступу для аутентифікації користувача.
    - session (AsyncSession): Об'єкт сеансу для з'єднання з базою даних.

    ## Повертає:
    - List[Contact]: Список контактів.

    """

    return await contacts.get_all_contacts(current_user, session)


@router.delete("/{contact_id}")
async def delete_contact(
    contact_id: int,
    current_user: User = Depends(auth_service.get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    # Видалити контакт.

    Видаляє контакт з вказаним ідентифікатором, якщо користувач з вказаним токеном доступу є власником контакту.

    ## Параметри:
    - contact_id (int): Ідентифікатор контакту, який потрібно видалити.
    - access_token (str): Токен доступу для аутентифікації користувача.
    - session (AsyncSession): Об'єкт сеансу для з'єднання з базою даних.

    ## Повертає:
    - dict: Результат видалення контакту у вигляді словника з повідомленням та видаленим контактом.

    """

    return await contacts.delete_contact(contact_id, current_user, session)


@router.put("/{contact_id}")
async def update_contact(
    contact_id: int,
    contact: ContactCreate,
    current_user: User = Depends(auth_service.get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    # Оновити контакт.

    Оновлює контакт з вказаним ідентифікатором, якщо користувач з вказаним токеном доступу є власником контакту.

    ## Параметри:
    - contact_id (int): Ідентифікатор контакту, який потрібно оновити.
    - contact (ContactCreate): Об'єкт, що містить нові дані для оновлення контакту.
    - access_token (str): Токен доступу для аутентифікації користувача.
    - session (AsyncSession): Об'єкт сеансу для з'єднання з базою даних.

    ## Повертає:
    - Contact: Оновлений об'єкт контакту.
    """

    return await contacts.update_contact(contact_id, contact, current_user, session)


@router.get("/birthdays/{days}")
async def get_upcoming_birthdays(
    days: int,
    current_user: User = Depends(auth_service.get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    # Отримати наближені дні народження контактів.

    ## Параметри:
    - days (int): Кількість днів для визначення наближених днів народження.
    - access_token (str, заголовок): Токен доступу для аутентифікації користувача.
    - session (AsyncSession, опціонально): Об'єкт сесії бази даних.

    ## Повертає:
    - результати (ResultProxy): Об'єкт, що містить результати запиту до бази даних.

    ## Raise:
    - HTTPException: Якщо користувач не автентифікований.
    """

    return await contacts.get_upcoming_birthdays(days, current_user, session)
