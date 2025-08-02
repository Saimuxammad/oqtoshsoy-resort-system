from pydantic import BaseModel, field_validator, ConfigDict
from datetime import date, datetime
from typing import Optional


class BookingBase(BaseModel):
    room_id: int
    start_date: date
    end_date: date
    guest_name: Optional[str] = None
    notes: Optional[str] = None

    @field_validator('end_date')
    @classmethod
    def validate_dates(cls, v, info):
        if 'start_date' in info.data and v < info.data['start_date']:
            raise ValueError('End date must be after start date')
        return v


class BookingCreate(BookingBase):
    pass


class BookingUpdate(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    guest_name: Optional[str] = None
    notes: Optional[str] = None


class RoomInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    room_number: str
    room_type: str


class Booking(BookingBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_by: int
    created_at: datetime
    updated_at: datetime
    room: Optional[RoomInfo] = None