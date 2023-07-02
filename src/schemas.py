from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, validator



class ContactBase(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone_number: str
    birthday: str
    additional_data: str = None

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
    username: str = Field(min_length=5, max_length=16)
    email: EmailStr
    password: str = Field(min_length=6, max_length=10)

class UserDb(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime
    avatar: str

    class Config:
        orm_mode = True

class UserResponse(BaseModel):
    user: UserDb
    detail: str = "User successfully created"

class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


