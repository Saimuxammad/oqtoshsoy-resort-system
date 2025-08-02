from pydantic import BaseModel, field_validator
from datetime import date, datetime
from typing import Optional


class BookingBase(BaseModel):
    room_id: int
    start_date: date
    end_date: date
    guest_name: Optional[str] = None
    notes: Optional[str] = None

    @validator('end_date')
    def validate_dates(cls, v, values):
        if 'start_date' in values and v < values['start_date']:
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
    id: int
    room_number: str
    room_type: str

    class Config:
        from_attributes = True


class Booking(BookingBase):
    id: int
    created_by: int
    created_at: datetime
    updated_at: datetime
    room: Optional[RoomInfo] = None

    class Config:
        from_attributes = True