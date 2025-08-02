"""
Конфигурация администраторов системы
Добавьте Telegram ID администраторов в соответствующие списки
"""

# Супер-администраторы (полный доступ + управление пользователями)
SUPER_ADMIN_IDS = [
    123456789,  # Замените на ваш Telegram ID
    # Добавьте другие ID супер-админов
]

# Обычные администраторы (управление бронированиями)
ADMIN_IDS = [
    987654321,  # Telegram ID админа 1
    456789123,  # Telegram ID админа 2
    # Добавьте другие ID админов
]

# Все разрешенные пользователи (если нужно ограничить доступ)
# Если список пустой - доступ разрешен всем
ALLOWED_USER_IDS = [
    # Оставьте пустым для открытого доступа
    # или добавьте ID разрешенных пользователей
]

def is_super_admin(telegram_id: int) -> bool:
    """Проверка, является ли пользователь супер-администратором"""
    return telegram_id in SUPER_ADMIN_IDS

def is_admin(telegram_id: int) -> bool:
    """Проверка, является ли пользователь администратором"""
    return telegram_id in ADMIN_IDS or telegram_id in SUPER_ADMIN_IDS

def is_allowed_user(telegram_id: int) -> bool:
    """Проверка, разрешен ли доступ пользователю"""
    if not ALLOWED_USER_IDS:  # Если список пустой - доступ всем
        return True
    return telegram_id in ALLOWED_USER_IDS or is_admin(telegram_id)