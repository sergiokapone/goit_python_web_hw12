from datetime import datetime
from typing import Dict, Union

from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator


class ContactBase(BaseModel):
    first_name: str = Field(...)
    last_name: str = Field(...)
    email: str = Field(...)
    phone_number: str = Field(...)
    birthday: str = Field(...)
    additional_data: str = Field(None)

    @field_validator("birthday")
    def validate_birthday(cls, value):
        try:
            datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Invalid date format. Expected format: YYYY-MM-DD")
        return value

    model_config = ConfigDict(
        json_schema_extra = {
            "title": "Contact Base",
            "description": "Base model for contact data",
            "example": {
                "first_name": "Sergiy",
                "last_name": "Ponomarenko",
                "email": "user@example.com",
                "phone_number": "0632569852",
                "birthday": "1978-12-12",
                "additional_data": "Physicist",
            },
        }
    )


class ContactCreate(ContactBase):
    pass


class Contact(ContactBase):
    model_config = ConfigDict(from_attributes=True)


class UserModel(BaseModel):
    username: str
    email: EmailStr
    password: str

    model_config = ConfigDict(
        json_schema_extra = {
            "title": "User Model",
            "description": "Model for user data",
            "example": {
                "username": "sergiokapone",
                "email": "example@example.com",
                "password": "qwer1234",
            },
        }
    )


class UserDb(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime
    avatar: str

    model_config = ConfigDict(
        json_schema_extra = {
            "example": {
                "id": 1,
                "username": "sergiokapone",
                "email": "user@example.com",
                "created_at": datetime.now(),
                "avatar": "https://example.com/avatar.jpg",
            }
        }
    )


class UserResponse(BaseModel):
    user: UserDb
    detail: str = "User successfully created"


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class LoginResponse(BaseModel):
    user: Dict[str, Union[str, str]] = Field(
        default={"username": "sergiokapone", "email": "user@example.com"}
    )
    access_token: str = Field(...)


class CucrrentUserResponse(BaseModel):
    username: str = Field(min_length=5, max_length=16, example="sergiokapone")
    email: EmailStr


class RequestEmail(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    new_password: str
