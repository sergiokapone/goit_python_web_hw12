import unittest
from unittest.mock import AsyncMock, MagicMock

from sqlalchemy.ext.asyncio import AsyncSession

from database import User, Contact
from repository import create_contact, get_all_contacts, delete_contact, update_contact
from schemas import ContactCreate


class TestAsync(unittest.IsolatedAsyncioTestCase):
    
    def setUp(self):
        self.session = AsyncMock(spec=AsyncSession)
        self.user = User(
            id=1, email="testuser@example.com", password="qwer1234", confirmed=True
        )
        self.contact = Contact(first_name = "John",
        last_name = "Doe",
        email = "johndoe@example.com",
        phone_number =  "123456789",
        birthday =  "2000-01-01",
        user_id = self.user.id)

    async def test_create_contact(self):
        body = self.contact
        result = await create_contact(body, self.user, self.session)
        self.assertEqual(result.first_name, body.first_name)
        self.assertEqual(result.last_name, body.last_name)

    async def test_get_all_contacts(self):
        expected_contacts = [self.contact]
        mock_contacts = MagicMock()
        mock_contacts.scalars.return_value.all.return_value = expected_contacts
        self.session.execute.return_value = mock_contacts
        result = await get_all_contacts(self.user, self.session)
        self.assertEqual(result, expected_contacts)

    async def test_update_contact_successful(self): 
            contact_id = 1
            contact_create = self.contact
            existing_contact = Contact(id=contact_id, user_id=self.user.id)
            
            session_mock = AsyncMock()
            session_mock.get.return_value = existing_contact

            updated_contact = await update_contact(contact_id, contact_create, self.user, session_mock)

            self.assertEqual(updated_contact.first_name, contact_create.first_name)
            self.assertEqual(updated_contact.last_name, contact_create.last_name)
            self.assertEqual(updated_contact.email, contact_create.email)
            self.assertEqual(updated_contact.phone_number, contact_create.phone_number)
            self.assertEqual(str(updated_contact.birthday), contact_create.birthday)
            self.assertEqual(updated_contact.additional_data, contact_create.additional_data)
            session_mock.commit.assert_called_once()
            session_mock.refresh.assert_called_once_with(existing_contact)

    async def test_delete_contact_successful(self):
            contact_id = 1
            contact = Contact(id=contact_id, user_id=self.user.id)
            
            session_mock = AsyncMock()
            session_mock.get.return_value = contact

            result = await delete_contact(contact_id, self.user, session_mock)

            self.assertEqual(result, {"message": "Contact deleted", "contact": contact})
            session_mock.delete.assert_called_once_with(contact)
            session_mock.commit.assert_called_once()

