# file: backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from .database import engine, Base
from .api import auth, rooms, bookings, users, websocket, analytics, export # ✅ Импортируем все роутеры

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Создаем все таблицы в БД при старте (если их нет)
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Приложение запускается...")
    yield
    logger.info("Приложение останавливается...")

app = FastAPI(
    title="Oqtoshsoy Resort Management API",
    version="2.0.1",
    description="Система управления бронированием Oqtoshsoy Resort",
    lifespan=lifespan,
    redirect_slashes=False
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # В реальном проекте лучше указать конкретный домен фронтенда
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Подключаем роутеры из папки /api
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(rooms.router, prefix="/api/rooms", tags=["Rooms"])
app.include_router(bookings.router, prefix="/api/bookings", tags=["Bookings"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(export.router, prefix="/api/export", tags=["Export"])
app.include_router(websocket.router, prefix="/api", tags=["WebSocket"])


@app.get("/api/health", tags=["System"])
async def health_check():
    """Проверка работоспособности API"""
    return {"status": "ok", "version": app.version}

@app.get("/", tags=["System"])
async def root():
    return {"message": "Welcome to Oqtoshsoy Resort API"}

# ❌ ВСЯ ЛОГИКА ОБРАБОТКИ КОМНАТ И БРОНИРОВАНИЙ ОТСЮДА УДАЛЕНА
# Теперь она находится в правильных файлах: api/rooms.py и api/bookings.py