# backend/config/admins.py
"""
Конфигурация пользователей системы и их ролей
СТРОГИЙ КОНТРОЛЬ ДОСТУПА
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

# Все разрешенные пользователи - ТОЛЬКО ЭТИ ID МОГУТ ВОЙТИ
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
    """
    ЖЕСТКАЯ ПРОВЕРКА ДОСТУПА
    Только пользователи из списка ALLOWED_USERS могут войти
    """
    # УБИРАЕМ ВСЕ ПРОВЕРКИ ПЕРЕМЕННЫХ - ВСЕГДА СТРОГИЙ РЕЖИМ!
    is_allowed = telegram_id in ALLOWED_USERS

    if not is_allowed:
        print(f"❌ ACCESS DENIED for Telegram ID: {telegram_id}")
        print(f"   This user is NOT in the allowed list!")
        print(f"   Allowed IDs: {ALLOWED_USERS}")
    else:
        print(f"✅ ACCESS GRANTED for Telegram ID: {telegram_id}")

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