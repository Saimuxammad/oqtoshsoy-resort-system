from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from ..database import Base
from datetime import datetime
import enum


class UserRole(enum.Enum):
    USER = "user"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String, nullable=True)
    username = Column(String, nullable=True)
    is_admin = Column(Boolean, default=False)
    role = Column(Enum(UserRole), default=UserRole.USER)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    bookings = relationship("Booking", back_populates="user")

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name or ''}".strip()

    @property
    def can_manage_bookings(self):
        return self.role in [UserRole.ADMIN, UserRole.SUPER_ADMIN] or self.is_admin

    @property
    def can_manage_users(self):
        return self.role == UserRole.SUPER_ADMIN