from sqlalchemy import Column, Integer, String, Float, Text, Enum as SQLEnum, DateTime
from sqlalchemy.orm import relationship
from ..database import Base
from datetime import datetime
import enum


class RoomType(enum.Enum):
    STANDARD_DOUBLE = "2 o'rinli standart"
    STANDARD_QUAD = "4 o'rinli standart"
    LUX_DOUBLE = "2 o'rinli lyuks"
    VIP_SMALL = "4 o'rinli kichik VIP"
    VIP_LARGE = "4 o'rinli katta VIP"
    APARTMENT = "4 o'rinli apartament"
    COTTAGE = "Kottedj (6 kishi uchun)"
    PRESIDENT = "Prezident apartamenti (8 kishi uchun)"


class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    room_number = Column(String, unique=True, index=True)
    room_type = Column(SQLEnum(RoomType))
    capacity = Column(Integer, nullable=False)  # Добавляем поле capacity
    price_per_night = Column(Float)
    description = Column(Text, nullable=True)
    amenities = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    bookings = relationship("Booking", back_populates="room")