"""
Скрипт для инициализации базы данных
Запустите: python -m app.init_db
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .database import Base, engine
from .models import room, booking, user, history
from .services.room_service import RoomService

def init_database():
    """Инициализация базы данных с начальными данными"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
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