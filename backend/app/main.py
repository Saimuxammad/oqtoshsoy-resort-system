from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
import uvicorn
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime

from .database import engine, get_db
from .models import room, booking, user, history
from .services.room_service import RoomService
from .services.notification_service import notification_service
from .api import rooms, bookings, auth, analytics, export, history as history_api, websocket

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
    db = next(get_db())
    RoomService.initialize_rooms(db)

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
    db = next(get_db())
    await notification_service.send_daily_report(db)


app = FastAPI(
    title="Oqtoshsoy Resort Management API",
    version="2.0.0",
    description="Advanced hotel management system with real-time updates",
    lifespan=lifespan,
    # ВАЖНО: Отключаем автоматическое добавление слешей
    redirect_slashes=False
)

# Configure CORS - ИСПРАВЛЕННАЯ КОНФИГУРАЦИЯ
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://oqtoshsoy-resort-system-production-ef7c.up.railway.app",
        "https://oqtoshsoy-resort-system-production.up.railway.app",
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:3000",
        "*"  # Временно разрешаем все источники для отладки
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(rooms.router, prefix="/api/rooms", tags=["rooms"])
app.include_router(bookings.router, prefix="/api/bookings", tags=["bookings"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
app.include_router(export.router, prefix="/api/export", tags=["export"])
app.include_router(history_api.router, prefix="/api/history", tags=["history"])
#app.include_router(websocket.router, prefix="/api", tags=["websocket"])


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
        "message": "API Root",
        "endpoints": {
            "auth": "/api/auth",
            "rooms": "/api/rooms",
            "bookings": "/api/bookings",
            "analytics": "/api/analytics",
            "export": "/api/export",
            "history": "/api/history"
        }
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}


# Добавляем обработку OPTIONS запросов для CORS preflight
@app.options("/{rest_of_path:path}")
async def preflight_handler(rest_of_path: str):
    return {"message": "OK"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)