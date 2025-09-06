# backend/app/config/admins.py
"""
Конфигурация пользователей системы и их ролей
СТРОГИЙ КОНТРОЛЬ ДОСТУПА
"""
import os

# КРИТИЧЕСКИ ВАЖНО: Читаем из переменной окружения
env_allowed_ids = os.getenv("ALLOWED_TELEGRAM_IDS", "")
print(f"[ADMINS CONFIG] Environment variable ALLOWED_TELEGRAM_IDS: {env_allowed_ids}")

# Парсим ID из переменной окружения
ALLOWED_IDS_FROM_ENV = []
if env_allowed_ids:
    try:
        for id_str in env_allowed_ids.split(","):
            id_str = id_str.strip()
            if id_str:
                telegram_id = int(id_str)
                ALLOWED_IDS_FROM_ENV.append(telegram_id)
                print(f"[ADMINS CONFIG] Added ID from env: {telegram_id}")
    except Exception as e:
        print(f"[ADMINS CONFIG] Error parsing ALLOWED_TELEGRAM_IDS: {e}")

# Если есть ID из переменной окружения, используем ТОЛЬКО их
if ALLOWED_IDS_FROM_ENV:
    print(f"[ADMINS CONFIG] Using {len(ALLOWED_IDS_FROM_ENV)} IDs from environment variable")
    SUPER_ADMINS = ALLOWED_IDS_FROM_ENV[:1]  # Первый ID - супер админ
    ADMINS = ALLOWED_IDS_FROM_ENV[1:2] if len(ALLOWED_IDS_FROM_ENV) > 1 else []
    MANAGERS = ALLOWED_IDS_FROM_ENV[2:3] if len(ALLOWED_IDS_FROM_ENV) > 2 else []
    OPERATORS = ALLOWED_IDS_FROM_ENV[3:] if len(ALLOWED_IDS_FROM_ENV) > 3 else []
else:
    print("[ADMINS CONFIG] WARNING: No IDs from environment, using hardcoded values")
    # Fallback на захардкоженные значения (только для разработки)
    SUPER_ADMINS = [5488749868]  # Ваш ID
    ADMINS = []
    MANAGERS = []
    OPERATORS = []

# Объединяем все списки
ALLOWED_USERS = SUPER_ADMINS + ADMINS + MANAGERS + OPERATORS

print(f"[ADMINS CONFIG] Final ALLOWED_USERS list: {ALLOWED_USERS}")
print(f"[ADMINS CONFIG] Total allowed users: {len(ALLOWED_USERS)}")


def is_allowed_user(telegram_id: int) -> bool:
    """
    ЖЕСТКАЯ ПРОВЕРКА ДОСТУПА
    Только пользователи из списка ALLOWED_USERS могут войти
    """
    # Преобразуем в int если пришла строка
    try:
        if isinstance(telegram_id, str):
            telegram_id = int(telegram_id)
    except:
        print(f"[ADMINS CONFIG] Invalid telegram_id format: {telegram_id}")
        return False

    # Проверяем в списке разрешенных
    is_allowed = telegram_id in ALLOWED_USERS

    # Детальное логирование
    print(f"[ADMINS CONFIG] Access check for ID {telegram_id}:")
    print(f"  - ALLOWED_USERS: {ALLOWED_USERS}")
    print(f"  - Is in list: {is_allowed}")

    if not is_allowed:
        print(f"[ADMINS CONFIG] ❌ ACCESS DENIED for Telegram ID: {telegram_id}")
        print(f"  - This ID is NOT in the allowed list!")
    else:
        print(f"[ADMINS CONFIG] ✅ ACCESS GRANTED for Telegram ID: {telegram_id}")

    return is_allowed


def is_super_admin(telegram_id: int) -> bool:
    """Проверяет, является ли пользователь супер-администратором"""
    try:
        if isinstance(telegram_id, str):
            telegram_id = int(telegram_id)
        return telegram_id in SUPER_ADMINS
    except:
        return False


def is_admin(telegram_id: int) -> bool:
    """Проверяет, является ли пользователь администратором"""
    try:
        if isinstance(telegram_id, str):
            telegram_id = int(telegram_id)
        return telegram_id in ADMINS or telegram_id in SUPER_ADMINS
    except:
        return False


def is_manager(telegram_id: int) -> bool:
    """Проверяет, является ли пользователь менеджером"""
    try:
        if isinstance(telegram_id, str):
            telegram_id = int(telegram_id)
        return telegram_id in MANAGERS
    except:
        return False


def is_operator(telegram_id: int) -> bool:
    """Проверяет, является ли пользователь оператором"""
    try:
        if isinstance(telegram_id, str):
            telegram_id = int(telegram_id)
        return telegram_id in OPERATORS
    except:
        return False


def get_user_role(telegram_id: int) -> str:
    """Возвращает роль пользователя"""
    try:
        if isinstance(telegram_id, str):
            telegram_id = int(telegram_id)

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
    except:
        return "user"