# Конфигурация администраторов и пользователей системы
# Telegram ID пользователей с разными ролями

# Супер-админы - полный доступ ко всему
SUPER_ADMINS = [
    123456789,  # Dev Admin (для тестирования)
    # Добавьте свой Telegram ID сюда
]

# Администраторы - почти полный доступ
ADMINS = [
    # Добавьте Telegram ID администраторов
]

# Менеджеры - управление бронированиями
MANAGERS = [
    # Добавьте Telegram ID менеджеров
]

# Операторы - создание и просмотр бронирований
OPERATORS = [
    # Добавьте Telegram ID операторов
]

# Разрешенные пользователи (если нужно ограничить доступ)
# Если список пустой - доступ разрешен всем
ALLOWED_USERS = []  # Оставьте пустым для открытого доступа


def is_super_admin(telegram_id: int) -> bool:
    """Проверка является ли пользователь супер-админом"""
    return telegram_id in SUPER_ADMINS


def is_admin(telegram_id: int) -> bool:
    """Проверка является ли пользователь админом"""
    return telegram_id in ADMINS or telegram_id in SUPER_ADMINS


def is_manager(telegram_id: int) -> bool:
    """Проверка является ли пользователь менеджером"""
    return telegram_id in MANAGERS or is_admin(telegram_id)


def is_operator(telegram_id: int) -> bool:
    """Проверка является ли пользователь оператором"""
    return telegram_id in OPERATORS or is_manager(telegram_id)


def is_allowed_user(telegram_id: int) -> bool:
    """Проверка разрешен ли доступ пользователю"""
    if not ALLOWED_USERS:  # Если список пустой - доступ всем
        return True
    return telegram_id in ALLOWED_USERS or is_operator(telegram_id)


def get_user_role(telegram_id: int) -> str:
    """Получить роль пользователя по Telegram ID"""
    if is_super_admin(telegram_id):
        return "super_admin"
    elif telegram_id in ADMINS:
        return "admin"
    elif telegram_id in MANAGERS:
        return "manager"
    elif telegram_id in OPERATORS:
        return "operator"
    else:
        return "user"