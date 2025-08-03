"""
Скрипт для инициализации базы данных
Запустите: python -m app.init_db
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .database import Base, engine
from .models import room, booking, user, history
from .services.room_service import RoomService
from .services.auth_service import get_password_hash


def init_database():
    """Инициализация базы данных с начальными данными"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        # Создаем администратора
        from .models.user import User
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            admin = User(
                telegram_id=123456789,
                username="admin",
                first_name="Admin",
                last_name="User",
                is_admin=True,
                password_hash=get_password_hash("admin123")
            )
            db.add(admin)
            db.commit()
            print("Admin user created")

        # Инициализируем комнаты
        print("Initializing rooms...")
        RoomService.initialize_rooms(db)
        print("Rooms initialized successfully")

    except Exception as e:
        print(f"Error initializing database: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    init_database()