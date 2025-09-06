# file: backend/create_admin.py
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Загружаем переменные окружения (важно для локального запуска, на Railway они уже есть)
load_dotenv()

# Получаем URL базы данных
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("❌ Ошибка: Переменная окружения DATABASE_URL не найдена.")
    exit()

# Railway использует postgres://, а SQLAlchemy требует postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Ваш ID и данные
ADMIN_TELEGRAM_ID = 5488749868
ADMIN_FIRST_NAME = "Admin"
ADMIN_USERNAME = "saimuxammad_admin"

try:
    # Подключаемся к базе данных
    engine = create_engine(DATABASE_URL)
    with engine.connect() as connection:
        print("✅ Успешно подключились к базе данных.")

        # Проверяем, существует ли уже пользователь
        check_query = text("SELECT id FROM users WHERE telegram_id = :id")
        result = connection.execute(check_query, {"id": ADMIN_TELEGRAM_ID}).fetchone()

        if result:
            print(f"ℹ️ Пользователь с Telegram ID {ADMIN_TELEGRAM_ID} уже существует.")
        else:
            # Если пользователя нет, создаем его
            print(f"✨ Пользователь с Telegram ID {ADMIN_TELEGRAM_ID} не найден. Создаем нового...")
            insert_query = text("""
                INSERT INTO users (telegram_id, first_name, username, is_admin, is_active, role, created_at, updated_at) 
                VALUES (:id, :name, :username, true, true, 'SUPER_ADMIN', NOW(), NOW())
            """)
            connection.execute(insert_query, {
                "id": ADMIN_TELEGRAM_ID,
                "name": ADMIN_FIRST_NAME,
                "username": ADMIN_USERNAME
            })
            # Важно: SQLAlchemy v2+ требует явного коммита для DML
            connection.commit()
            print(f"✅ Успешно создан пользователь-администратор для Telegram ID {ADMIN_TELEGRAM_ID}!")

except Exception as e:
    print(f"❌ Произошла ошибка: {e}")
    exit(1) # Выход с ошибкой, чтобы деплой мог остановиться, если что-то не так