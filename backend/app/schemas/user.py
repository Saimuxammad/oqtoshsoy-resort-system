from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from enum import Enum


class UserRoleEnum(str, Enum):
    USER = "user"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


class UserBase(BaseModel):
    telegram_id: int
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None
    is_admin: bool = False
    role: UserRoleEnum = UserRoleEnum.USER
    is_active: bool = True


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    is_admin: Optional[bool] = None
    role: Optional[UserRoleEnum] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
    can_manage_bookings: bool = False
    can_manage_users: bool = False


class TelegramAuthData(BaseModel):
    initData: str