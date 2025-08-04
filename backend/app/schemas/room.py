from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime
from enum import Enum


class RoomStatus(str, Enum):
    available = "available"
    occupied = "occupied"
    maintenance = "maintenance"


class RoomBase(BaseModel):
    room_number: str
    room_type: Any  # Изменено на Any для поддержки enum
    capacity: int
    price_per_night: float
    description: Optional[str] = None
    amenities: Optional[str] = None


class RoomCreate(RoomBase):
    pass


class RoomUpdate(BaseModel):
    description: Optional[str] = None
    amenities: Optional[str] = None
    price_per_night: Optional[float] = None


class Room(RoomBase):
    id: int
    created_at: datetime
    updated_at: datetime
    is_available: Optional[bool] = True  # Значение по умолчанию
    current_booking: Optional[dict] = None

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True  # Разрешаем произвольные типы