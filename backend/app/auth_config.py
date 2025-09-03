# backend/app/auth_config.py
"""
Конфигурация пользователей и их ролей
"""

# Предустановленные пользователи системы
USERS = {
    # Администратор - полный доступ
    "admin": {
        "password": "admin123",  # В продакшене используйте хешированные пароли!
        "role": "Administrator",
        "name": "Admin",
        "permissions": ["create", "read", "update", "delete", "analytics", "settings"]
    },

    # Менеджер - может управлять бронированиями
    "manager": {
        "password": "manager123",
        "role": "Manager",
        "name": "Menejer",
        "permissions": ["create", "read", "update", "delete", "analytics"]
    },

    # Оператор - может создавать и просматривать
    "operator1": {
        "password": "operator123",
        "role": "Operator",
        "name": "Operator 1",
        "permissions": ["create", "read", "update"]
    },

    # Оператор 2
    "operator2": {
        "password": "operator123",
        "role": "Operator",
        "name": "Operator 2",
        "permissions": ["create", "read", "update"]
    },

    # Наблюдатель - только просмотр
    "viewer": {
        "password": "viewer123",
        "role": "Viewer",
        "name": "Kuzatuvchi",
        "permissions": ["read"]
    }
}

# Описание ролей
ROLES = {
    "Administrator": {
        "name_uz": "Administrator",
        "description": "To'liq huquq - barcha funksiyalardan foydalanish",
        "can_delete": True,
        "can_modify_settings": True,
        "can_view_analytics": True
    },
    "Manager": {
        "name_uz": "Menejer",
        "description": "Bronlarni boshqarish, tahlil ko'rish",
        "can_delete": True,
        "can_modify_settings": False,
        "can_view_analytics": True
    },
    "Operator": {
        "name_uz": "Operator",
        "description": "Bronlarni yaratish va tahrirlash",
        "can_delete": False,
        "can_modify_settings": False,
        "can_view_analytics": False
    },
    "Viewer": {
        "name_uz": "Kuzatuvchi",
        "description": "Faqat ko'rish huquqi",
        "can_delete": False,
        "can_modify_settings": False,
        "can_view_analytics": False
    }
}


def check_permission(username: str, permission: str) -> bool:
    """Foydalanuvchining ruxsatini tekshirish"""
    if username not in USERS:
        return False
    return permission in USERS[username]["permissions"]


def get_user_role(username: str) -> dict:
    """Foydalanuvchi rolini olish"""
    if username not in USERS:
        return None
    role_name = USERS[username]["role"]
    return ROLES.get(role_name)