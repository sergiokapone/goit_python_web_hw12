
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
        
    email = auth_service.extract_email_from_token(access_token)

    return await contacts.create_contact(contact, email, session)

@router.get("/")
async def get_all_contacts(
    access_token: str = Header(...,
                                description="Введіть токен доступу",
                                convert_underscores=False),
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
    
    email = auth_service.extract_email_from_token(access_token)

    return await contacts.get_all_contacts(email, session)

@router.delete("/{contact_id}")
async def delete_contact(contact_id: int,
                         access_token: str = Header(...,
                                description="Введіть токен доступу",
                                convert_underscores=False),
                      session: AsyncSession = Depends(get_session)):
    
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


    email = auth_service.extract_email_from_token(access_token)

    return await contacts.delete_contact(contact_id, email, session)


@router.put("/{contact_id}")
async def delete_contact(contact_id: int,
                         contact: ContactCreate,
                         access_token: str = Header(...,
                                description="Введіть токен доступу",
                                convert_underscores=False),
                      session: AsyncSession = Depends(get_session)):
    
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
        
    
    email = auth_service.extract_email_from_token(access_token)

    return await contacts.update_contact(contact_id, contact, email, session)