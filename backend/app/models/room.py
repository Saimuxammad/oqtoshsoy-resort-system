from sqlalchemy import Column, Integer, String, Float, Text, DateTime
from sqlalchemy.orm import relationship
from ..database import Base
from datetime import datetime


class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    room_number = Column(String, unique=True, index=True)
    # Используем String вместо Enum для избежания проблем с PostgreSQL
    room_type = Column(String, nullable=False)
    capacity = Column(Integer, nullable=False, default=2)
    price_per_night = Column(Float, default=500000)
    description = Column(Text, nullable=True)
    amenities = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    bookings = relationship("Booking", back_populates="room")