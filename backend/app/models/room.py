from sqlalchemy import Column, Integer, String, Boolean, Enum, DateTime
from sqlalchemy.orm import relationship
from ..database import Base
import enum
from datetime import datetime


class RoomType(str, enum.Enum):
    STANDARD_2 = "2 o'rinli standart"
    STANDARD_4 = "4 o'rinli standart"
    LUX_2 = "2 o'rinli lyuks"
    VIP_SMALL_4 = "4 o'rinli kichik VIP"
    VIP_BIG_4 = "4 o'rinli katta VIP"
    APARTMENT_4 = "4 o'rinli apartament"
    COTTAGE_6 = "Kottedj (6 kishi uchun)"
    PRESIDENT_8 = "Prezident apartamenti (8 kishi uchun)"


class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    room_number = Column(String, unique=True, index=True)
    room_type = Column(Enum(RoomType))
    is_available = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    bookings = relationship("Booking", back_populates="room")