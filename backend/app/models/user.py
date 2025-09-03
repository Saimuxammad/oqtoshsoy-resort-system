from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from ..database import Base
from datetime import datetime
import enum


class UserRole(enum.Enum):
    SUPER_ADMIN = "super_admin"  # Полный доступ
    ADMIN = "admin"  # Администратор
    MANAGER = "manager"  # Менеджер
    OPERATOR = "operator"  # Оператор
    USER = "user"  # Обычный пользователь


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, index=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    username = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)

    # Роль пользователя
    role = Column(SQLEnum(UserRole), default=UserRole.USER)
    is_admin = Column(Boolean, default=False)  # Для обратной совместимости
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Связи
    bookings = relationship("Booking", back_populates="user")

    def has_permission(self, permission: str) -> bool:
        """Проверка разрешений на основе роли"""
        permissions = {
            UserRole.SUPER_ADMIN: [
                "view_all", "create_booking", "edit_booking", "delete_booking",
                "view_analytics", "manage_users", "system_settings", "export_data"
            ],
            UserRole.ADMIN: [
                "view_all", "create_booking", "edit_booking", "delete_booking",
                "view_analytics", "manage_users", "export_data"
            ],
            UserRole.MANAGER: [
                "view_all", "create_booking", "edit_booking", "delete_own_booking",
                "view_analytics", "export_data"
            ],
            UserRole.OPERATOR: [
                "view_all", "create_booking", "edit_own_booking"
            ],
            UserRole.USER: [
                "view_own", "create_booking"
            ]
        }

        return permission in permissions.get(self.role, [])

    def can_delete_booking(self, booking) -> bool:
        """Проверка может ли пользователь удалить бронирование"""
        if self.role in [UserRole.SUPER_ADMIN, UserRole.ADMIN]:
            return True
        elif self.role == UserRole.MANAGER:
            return booking.created_by == self.id
        else:
            return False

    def can_edit_booking(self, booking) -> bool:
        """Проверка может ли пользователь редактировать бронирование"""
        if self.role in [UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.MANAGER]:
            return True
        elif self.role == UserRole.OPERATOR:
            return booking.created_by == self.id
        else:
            return False