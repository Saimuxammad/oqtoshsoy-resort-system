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
    "http://localhost:3000"
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
        # Попробуем подсчитать количество комнат
        from .models.room import Room
        count = db.query(Room).count()
        return {"status": "ok", "rooms_count": count}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/api/test-room")
async def test_room(db: Session = Depends(get_db)):
    """Test getting one room"""
    try:
        from .models.room import Room
        room = db.query(Room).first()
        if room:
            return {
                "id": room.id,
                "room_number": room.room_number,
                "room_type": str(room.room_type),
                "room_type_value": room.room_type.value if hasattr(room.room_type, 'value') else None,
                "capacity": room.capacity,
                "price": float(room.price_per_night) if room.price_per_night else 0
            }
        return {"status": "no_rooms"}
    except Exception as e:
        return {"status": "error", "message": str(e), "type": str(type(e))}


@app.get("/api/init-rooms")
async def init_rooms(db: Session = Depends(get_db)):
    """Initialize rooms in database"""
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


@app.get("/api/fix-capacity")
async def fix_capacity(db: Session = Depends(get_db)):
    """Fix capacity field in rooms"""
    try:
        from sqlalchemy import text

        # Проверяем, есть ли колонка capacity
        result = db.execute(text("""
                                 SELECT column_name
                                 FROM information_schema.columns
                                 WHERE table_name = 'rooms'
                                   AND column_name = 'capacity'
                                 """))

        if result.fetchone() is None:
            # Добавляем колонку
            db.execute(text("ALTER TABLE rooms ADD COLUMN capacity INTEGER DEFAULT 2"))
            db.commit()

            # Обновляем значения используя ENUM имена
            capacity_map = {
                "STANDARD_DOUBLE": 2,
                "STANDARD_QUAD": 4,
                "LUX_DOUBLE": 2,
                "VIP_SMALL": 4,
                "VIP_LARGE": 4,
                "APARTMENT": 4,
                "COTTAGE": 6,
                "PRESIDENT": 8
            }

            for room_type, capacity in capacity_map.items():
                db.execute(
                    text(f"UPDATE rooms SET capacity = :capacity WHERE room_type = '{room_type}'"),
                    {"capacity": capacity}
                )
            db.commit()
            return {"status": "fixed", "message": "Capacity column added"}
        else:
            # Если колонка уже есть, просто обновим значения
            db.execute(text("UPDATE rooms SET capacity = 2 WHERE capacity IS NULL"))
            db.commit()
            return {"status": "updated", "message": "Set default capacity for null values"}
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}


@app.get("/api/rooms-simple")
async def get_rooms_simple(db: Session = Depends(get_db)):
    """Simple endpoint to get rooms without complex serialization"""
    try:
        from .models.room import Room
        rooms = db.query(Room).all()
        result = []

        for room in rooms:
            # Получаем capacity безопасно
            capacity = 2  # значение по умолчанию
            if hasattr(room, 'capacity') and room.capacity is not None:
                capacity = room.capacity

            # Обрабатываем room_type
            if hasattr(room.room_type, 'value'):
                room_type_str = room.room_type.value
            else:
                room_type_str = str(room.room_type)

            result.append({
                "id": room.id,
                "room_number": room.room_number,
                "room_type": room_type_str,
                "capacity": capacity,
                "price_per_night": float(room.price_per_night) if room.price_per_night else 0,
                "description": room.description or "",
                "amenities": room.amenities or "",
                "is_available": True
            })

        return result
    except Exception as e:
        return {"error": str(e), "type": str(type(e))}


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