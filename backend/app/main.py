from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
import uvicorn
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
import logging
import os

from .database import engine, get_db
from .models import room, booking, user, history
from .services.room_service import RoomService
from .services.notification_service import notification_service
from .api import rooms, bookings, auth, analytics, export, history as history_api

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create tables
room.Base.metadata.create_all(bind=engine)
booking.Base.metadata.create_all(bind=engine)
user.Base.metadata.create_all(bind=engine)
history.Base.metadata.create_all(bind=engine)

# Create scheduler for daily reports
scheduler = AsyncIOScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        db = next(get_db())
        RoomService.initialize_rooms(db)
        logger.info("Rooms initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing rooms: {e}")

    # Schedule daily report at 9:00 AM
    scheduler.add_job(
        send_daily_report,
        'cron',
        hour=9,
        minute=0,
        id='daily_report'
    )
    scheduler.start()

    yield
    # Shutdown
    scheduler.shutdown()


async def send_daily_report():
    """Send daily report to admins"""
    try:
        db = next(get_db())
        await notification_service.send_daily_report(db)
    except Exception as e:
        logger.error(f"Error sending daily report: {e}")


app = FastAPI(
    title="Oqtoshsoy Resort Management API",
    version="2.0.0",
    description="Advanced hotel management system with real-time updates",
    lifespan=lifespan,
    redirect_slashes=False
)

# Настройка CORS - ПОЛНАЯ поддержка
origins = [
    "https://oqtoshsoy-resort-system-production-ef7c.up.railway.app",
    "https://oqtoshsoy-resort-system-production.up.railway.app",
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:3000",
    "*"  # Временно разрешаем все источники для отладки
]

# Добавляем frontend URL из переменной окружения
frontend_url = os.getenv("FRONTEND_URL")
if frontend_url and frontend_url not in origins:
    origins.append(frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600
)

# Добавляем middleware для доверенных хостов
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # В production укажите конкретные домены
)

# Include routers с правильными префиксами
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(rooms.router, prefix="/api/rooms", tags=["rooms"])
app.include_router(bookings.router, prefix="/api/bookings", tags=["bookings"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
app.include_router(export.router, prefix="/api/export", tags=["export"])
app.include_router(history_api.router, prefix="/api/history", tags=["history"])


@app.get("/")
async def root():
    return {
        "message": "Oqtoshsoy Resort Management System API",
        "version": "2.0.0",
        "status": "active",
        "features": [
            "Real-time updates via WebSocket",
            "Telegram notifications",
            "Analytics and reporting",
            "Excel export",
            "History tracking",
            "Multi-language support (UZ/RU)"
        ]
    }


@app.get("/api")
async def api_root():
    """API root endpoint"""
    return {
        "message": "API is running",
        "version": "2.0.0",
        "endpoints": {
            "auth": "/api/auth",
            "rooms": "/api/rooms",
            "bookings": "/api/bookings",
            "analytics": "/api/analytics",
            "export": "/api/export",
            "history": "/api/history"
        }
    }


@app.get("/api/test")
async def test_endpoint():
    """Test endpoint to check if API is working"""
    return {"status": "ok", "message": "API is working"}


@app.get("/api/test-db")
async def test_database(db: Session = Depends(get_db)):
    """Test database connection"""
    try:
        from .models.room import Room
        count = db.query(Room).count()
        return {"status": "ok", "rooms_count": count}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/api/init-rooms")
async def init_rooms(db: Session = Depends(get_db)):
    """Initialize rooms in database if empty"""
    try:
        from .models.room import Room
        # Проверяем, есть ли уже комнаты
        count = db.query(Room).count()
        if count > 0:
            return {"status": "already_initialized", "rooms_count": count}

        # Инициализируем комнаты
        RoomService.initialize_rooms(db)
        new_count = db.query(Room).count()
        return {"status": "initialized", "rooms_count": new_count}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/api/fix-database")
async def fix_database(db: Session = Depends(get_db)):
    """Fix all missing columns in rooms table"""
    try:
        from sqlalchemy import text

        # Список колонок, которые должны быть в таблице
        required_columns = {
            'capacity': 'INTEGER DEFAULT 2',
            'price_per_night': 'FLOAT DEFAULT 500000',
            'description': 'TEXT',
            'amenities': 'TEXT',
            'created_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
            'updated_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
        }

        added_columns = []

        for column_name, column_type in required_columns.items():
            # Проверяем, существует ли колонка
            result = db.execute(text(f"""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='rooms' AND column_name='{column_name}'
            """))

            if result.fetchone() is None:
                # Добавляем колонку
                db.execute(text(f"ALTER TABLE rooms ADD COLUMN {column_name} {column_type}"))
                db.commit()
                added_columns.append(column_name)

        # Устанавливаем цены по умолчанию для разных типов комнат
        from .models.room import RoomType

        price_map = {
            RoomType.STANDARD_DOUBLE: 500000,
            RoomType.STANDARD_QUAD: 700000,
            RoomType.LUX_DOUBLE: 800000,
            RoomType.VIP_SMALL: 1000000,
            RoomType.VIP_LARGE: 1200000,
            RoomType.APARTMENT: 1500000,
            RoomType.COTTAGE: 2000000,
            RoomType.PRESIDENT: 3000000
        }

        for room_type, price in price_map.items():
            db.execute(
                text(
                    f"UPDATE rooms SET price_per_night = :price WHERE room_type = :room_type AND price_per_night IS NULL"),
                {"price": price, "room_type": room_type.name}
            )

        # Устанавливаем capacity по умолчанию
        capacity_map = {
            RoomType.STANDARD_DOUBLE: 2,
            RoomType.STANDARD_QUAD: 4,
            RoomType.LUX_DOUBLE: 2,
            RoomType.VIP_SMALL: 4,
            RoomType.VIP_LARGE: 4,
            RoomType.APARTMENT: 4,
            RoomType.COTTAGE: 6,
            RoomType.PRESIDENT: 8
        }

        for room_type, capacity in capacity_map.items():
            db.execute(
                text(f"UPDATE rooms SET capacity = :capacity WHERE room_type = :room_type AND capacity IS NULL"),
                {"capacity": capacity, "room_type": room_type.name}
            )

        db.commit()

        return {
            "status": "success",
            "added_columns": added_columns,
            "message": f"Added {len(added_columns)} columns and updated default values"
        }
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}


# Обработчик для всех несуществующих маршрутов
@app.exception_handler(404)
async def not_found_handler(request, exc):
    logger.warning(f"404 Not Found: {request.url}")
    return {
        "detail": f"Path {request.url.path} not found",
        "status_code": 404
    }


# Обработчик для внутренних ошибок сервера
@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error(f"500 Internal Server Error: {exc}")
    return {
        "detail": "Internal server error",
        "status_code": 500
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)


@app.get("/api/migrate-room-types")
async def migrate_room_types(db: Session = Depends(get_db)):
    """Migrate room types from enum to string"""
    try:
        from sqlalchemy import text

        # Получаем текущие комнаты
        result = db.execute(text("SELECT id, room_type::text FROM rooms"))
        rooms = result.fetchall()

        # Мапинг старых значений на новые
        type_map = {
            'STANDARD_DOUBLE': "2 o'rinli standart",
            'STANDARD_QUAD': "4 o'rinli standart",
            'LUX_DOUBLE': "2 o'rinli lyuks",
            'VIP_SMALL': "4 o'rinli kichik VIP",
            'VIP_LARGE': "4 o'rinli katta VIP",
            'APARTMENT': "4 o'rinli apartament",
            'COTTAGE': "Kottedj (6 kishi uchun)",
            'PRESIDENT': "Prezident apartamenti (8 kishi uchun)"
        }

        updated = 0
        for room_id, room_type in rooms:
            new_type = type_map.get(room_type, room_type)
            # Используем параметризованный запрос для безопасности
            db.execute(
                text("UPDATE rooms SET room_type = :new_type WHERE id = :room_id"),
                {"new_type": new_type, "room_id": room_id}
            )
            updated += 1

        db.commit()

        return {
            "status": "success",
            "message": f"Updated {updated} rooms",
            "rooms_migrated": updated
        }
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}