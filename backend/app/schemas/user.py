from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    telegram_id: int
    username: Optional[str] = None
    first_name: str
    last_name: Optional[str] = None
    is_admin: bool = False


class UserCreate(UserBase):
    password: Optional[str] = None


class UserLogin(BaseModel):
    username: str
    password: str


class User(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    id: int
    telegram_id: int
    username: Optional[str] = None
    first_name: str
    last_name: Optional[str] = None
    is_admin: bool = False
    created_at: datetime

    class Config:
        from_attributes = True


class TelegramAuthData(BaseModel):
    id: int
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None
    photo_url: Optional[str] = None
    auth_date: int
    hash: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    telegram_id: Optional[int] = None