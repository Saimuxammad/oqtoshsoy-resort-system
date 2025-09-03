# backend/config/admins.py
"""
Конфигурация пользователей системы и их ролей
"""

# Telegram IDs администраторов и пользователей
# Замените эти ID на реальные Telegram ID ваших пользователей

SUPER_ADMINS = [
    5488749868,  # Главный администратор - замените на ваш Telegram ID
]

ADMINS = [
    123456789,  # Администратор 1
    # 987654321,  # Администратор 2 (добавьте при необходимости)
]

MANAGERS = [
    # 111111111,  # Менеджер 1
]

OPERATORS = [
    # 222222222,  # Оператор 1
    # 333333333,  # Оператор 2
]

# Все разрешенные пользователи (3-4 человека как вы указали)
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
    # В режиме разработки разрешаем доступ всем
    import os
    if os.getenv("ENVIRONMENT", "development") == "development":
        return True

    # В продакшене проверяем список разрешенных пользователей
    return telegram_id in ALLOWED_USERS


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