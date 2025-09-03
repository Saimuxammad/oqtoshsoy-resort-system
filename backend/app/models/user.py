from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from ..database import Base
from datetime import datetime
import enum


class UserRole(enum.Enum):
    USER = "user"  # Обычный пользователь (только просмотр)
    OPERATOR = "operator"  # Оператор (создание бронирований)
    MANAGER = "manager"  # Менеджер (создание/редактирование)
    ADMIN = "admin"  # Администратор (полный доступ)
    SUPER_ADMIN = "super_admin"  # Супер-админ (управление пользователями)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String, nullable=True)
    username = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    is_admin = Column(Boolean, default=False)  # Для обратной совместимости
    role = Column(Enum(UserRole), default=UserRole.USER)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    bookings = relationship("Booking", back_populates="user")

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name or ''}".strip()

    # Права доступа на основе ролей
    @property
    def can_view_rooms(self):
        """Просмотр комнат - все роли"""
        return True

    @property
    def can_create_bookings(self):
        """Создание бронирований - от Оператора и выше"""
        return self.role in [UserRole.OPERATOR, UserRole.MANAGER, UserRole.ADMIN, UserRole.SUPER_ADMIN]

    @property
    def can_edit_bookings(self):
        """Редактирование бронирований - от Менеджера и выше"""
        return self.role in [UserRole.MANAGER, UserRole.ADMIN, UserRole.SUPER_ADMIN]

    @property
    def can_delete_bookings(self):
        """Удаление бронирований - от Менеджера и выше"""
        return self.role in [UserRole.MANAGER, UserRole.ADMIN, UserRole.SUPER_ADMIN]

    @property
    def can_delete_any_booking(self):
        """Удаление любых бронирований - только Админ и выше"""
        return self.role in [UserRole.ADMIN, UserRole.SUPER_ADMIN]

    @property
    def can_view_analytics(self):
        """Просмотр аналитики - от Менеджера и выше"""
        return self.role in [UserRole.MANAGER, UserRole.ADMIN, UserRole.SUPER_ADMIN]

    @property
    def can_export_data(self):
        """Экспорт данных - от Менеджера и выше"""
        return self.role in [UserRole.MANAGER, UserRole.ADMIN, UserRole.SUPER_ADMIN]

    @property
    def can_manage_settings(self):
        """Управление настройками - только Админ и выше"""
        return self.role in [UserRole.ADMIN, UserRole.SUPER_ADMIN]

    @property
    def can_manage_users(self):
        """Управление пользователями - только Супер-админ"""
        return self.role == UserRole.SUPER_ADMIN

    @property
    def can_view_history(self):
        """Просмотр истории - от Менеджера и выше"""
        return self.role in [UserRole.MANAGER, UserRole.ADMIN, UserRole.SUPER_ADMIN]

    def can_modify_booking(self, booking):
        """Проверка прав на изменение конкретного бронирования"""
        if self.can_delete_any_booking:
            return True  # Админ может изменять любые
        if self.can_edit_bookings:
            return booking.created_by == self.id  # Менеджер только свои
        return False

    def get_role_display(self):
        """Отображаемое название роли"""
        role_names = {
            UserRole.USER: "Foydalanuvchi",
            UserRole.OPERATOR: "Operator",
            UserRole.MANAGER: "Menejer",
            UserRole.ADMIN: "Administrator",
            UserRole.SUPER_ADMIN: "Super Administrator"
        }
        return role_names.get(self.role, "Noma'lum")