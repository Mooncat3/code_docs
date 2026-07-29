from typing import Optional

from pydantic import BaseModel, EmailStr, Field
from uuid import UUID

USERNAME_PATTERN = r"^[0-9a-zA-Z_]{3,32}$"
PASSWORD_PATTERN = r"^[0-9a-zA-Z!\"#$%&'()*+,-.\/:;<=>?@\\[\\]^_`{|}~]{8,32}$"


class UserBase(BaseModel):
    username: str = Field(..., max_length=32, min_length=3, pattern=USERNAME_PATTERN)
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(..., max_length=32, min_length=8, pattern=PASSWORD_PATTERN)


class UserUpdate(BaseModel):
    is_active: Optional[bool] = None


class UserLogin(BaseModel):
    username: str = Field(..., max_length=32, min_length=3, pattern=USERNAME_PATTERN)
    password: str = Field(..., max_length=32, min_length=8, pattern=PASSWORD_PATTERN)


class UserOwner(BaseModel):
    id: UUID


class User(UserBase):
    id: UUID
    is_active: bool
    role: str
    register_timestamp: int

    class Config:
        from_attributes = True
