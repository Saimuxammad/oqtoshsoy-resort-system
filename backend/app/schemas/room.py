from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional, List
from ..models.room import RoomType


class BookingInfo(BaseModel):
    id: int
    start_date: date
    end_date: date
    guest_name: Optional[str] = None

    class Config:
        from_attributes = True


class RoomBase(BaseModel):
    room_number: str
    room_type: RoomType


class RoomCreate(RoomBase):
    pass


class RoomUpdate(BaseModel):
    is_available: Optional[bool] = None


class Room(RoomBase):
    id: int
    is_available: bool
    current_booking: Optional[BookingInfo] = None
    upcoming_bookings: List[BookingInfo] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True