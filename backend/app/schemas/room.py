from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List
from enum import Enum


class RoomTypeEnum(str, Enum):
    STANDARD_2 = "2 o'rinli standart"
    STANDARD_4 = "4 o'rinli standart"
    LUX_2 = "2 o'rinli lyuks"
    VIP_SMALL_4 = "4 o'rinli kichik VIP"
    VIP_BIG_4 = "4 o'rinli katta VIP"
    APARTMENT_4 = "4 o'rinli apartament"
    COTTAGE_6 = "Kottedj (6 kishi uchun)"
    PRESIDENT_8 = "Prezident apartamenti (8 kishi uchun)"


class RoomBase(BaseModel):
    room_number: str
    room_type: RoomTypeEnum
    capacity: int
    price_per_night: Optional[float] = None
    description: Optional[str] = None


class RoomCreate(RoomBase):
    pass


class RoomUpdate(BaseModel):
    room_number: Optional[str] = None
    room_type: Optional[RoomTypeEnum] = None
    capacity: Optional[int] = None
    price_per_night: Optional[float] = None
    description: Optional[str] = None


class BookingInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    start_date: str
    end_date: str
    guest_name: Optional[str] = None


class Room(RoomBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_available: bool
    created_at: datetime
    updated_at: datetime
    current_booking: Optional[BookingInfo] = None
    bookings: List[BookingInfo] = []