from app.config import settings
from sqlalchemy import create_engine, text

try:
    engine = create_engine(settings.database_url)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print("✅ Database connection successful!")

        # Проверяем таблицы
        result = conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname='public'"))
        tables = [row[0] for row in result]
        print(f"📋 Tables in database: {tables}")

        # Проверяем количество комнат
        if 'rooms' in tables:
            result = conn.execute(text("SELECT COUNT(*) FROM rooms"))
            count = result.scalar()
            print(f"🏨 Rooms in database: {count}")

except Exception as e:
    print(f"❌ Database connection failed: {e}")