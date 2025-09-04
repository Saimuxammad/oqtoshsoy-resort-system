# backend/config/admins.py
"""
Конфигурация пользователей системы и их ролей
"""
import os

# Telegram IDs администраторов и пользователей
SUPER_ADMINS = [
    5488749868,  # Ваш Telegram ID
]

ADMINS = [
    # Добавьте сюда ID других администраторов если нужно
]

MANAGERS = [
    # Добавьте сюда ID менеджеров если нужно
]

OPERATORS = [
    # Добавьте сюда ID операторов если нужно
]

# Все разрешенные пользователи (3-4 человека)
ALLOWED_USERS = SUPER_ADMINS + ADMINS + MANAGERS + OPERATORS


def is_super_admin(telegram_id: int) -> bool:
    """Проверяет, является ли пользователь супер-администратором"""
    return telegram_id in SUPER_ADMINS


def is_admin(telegram_id: int) -> bool:
    """Проверяет, является ли пользователь администратором"""
    return telegram_id in ADMINS or telegram_id in SUPER_ADMINS


def is_manager(telegram_id: int) -> bool:
    """Проверяет, является ли пользователь менеджером"""
    return telegram_id in MANAGERS


def is_operator(telegram_id: int) -> bool:
    """Проверяет, является ли пользователь оператором"""
    return telegram_id in OPERATORS


def is_allowed_user(telegram_id: int) -> bool:
    """Проверяет, разрешен ли доступ пользователю к системе"""
    # Используем отдельную переменную для контроля доступа
    access_control = os.getenv("ACCESS_CONTROL", "strict")

    # Если ACCESS_CONTROL=open, пускаем всех (только для тестирования!)
    if access_control == "open":
        print(f"WARNING: Access control is OPEN! User {telegram_id} allowed.")
        return True

    # По умолчанию и при ACCESS_CONTROL=strict проверяем список
    is_allowed = telegram_id in ALLOWED_USERS

    if not is_allowed:
        print(f"Access DENIED for Telegram ID: {telegram_id}")
        print(f"Add this ID to ALLOWED_USERS to grant access")
    else:
        print(f"Access GRANTED for Telegram ID: {telegram_id}")

    return is_allowed


def get_user_role(telegram_id: int) -> str:
    """Возвращает роль пользователя"""
    if is_super_admin(telegram_id):
        return "super_admin"
    elif is_admin(telegram_id):
        return "admin"
    elif is_manager(telegram_id):
        return "manager"
    elif is_operator(telegram_id):
        return "operator"
    else:
        return "user"