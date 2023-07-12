from typing import Dict, Union

from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, validator



class ContactBase(BaseModel):
    first_name: str = Field(..., example="Sergiy")
    last_name: str = Field(..., example="Ponomarenko")
    email: str = Field(..., example="user@example.com")
    phone_number: str = Field(..., example="0632569852")
    birthday: str = Field(..., example="1978-12-12")
    additional_data: str = Field(None, example="Physicist")

    @validator("birthday")
    def validate_birthday(cls, value):
        try:
            datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Invalid date format. Expected format: YYYY-MM-DD")
        return value


class ContactCreate(ContactBase):
    pass


class Contact(ContactBase):
    class Config:
        orm_mode = True


class UserModel(BaseModel):
    username: str = Field(min_length=5, max_length=16, example="sergiokapone")
    email: EmailStr
    password: str = Field(min_length=6, max_length=10, example="qwer1234")

class UserDb(BaseModel):
    id: int = Field(..., example=1)
    username: str = Field(..., example="sergiokapone")
    email: str = Field(..., example="user@example.com")
    created_at: datetime = Field(..., example=datetime.now())
    avatar: str = Field(..., example="https://example.com/avatar.jpg")

    class Config:
        orm_mode = True

class UserResponse(BaseModel):
    user: UserDb
    detail: str = "User successfully created"

class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class LoginResponse(BaseModel):
    user: Dict[str, Union[str, str]] = Field(
        default={
            "username": "sergiokapone", 
            "email": "user@example.com"
            })
    access_token: str = Field(...)

class CucrrentUserResponse(BaseModel):
    username: str = Field(
        min_length=5, 
        max_length=16, 
        example="sergiokapone")
    email: EmailStr


class RequestEmail(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    new_password: str