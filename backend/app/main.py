from fastapi import FastAPI, HTTPException, Depends, APIRouter, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
import uvicorn
from datetime import datetime, date, timedelta
import logging
import os
from typing import Optional, List
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
import io
import pandas as pd
import secrets

from .database import engine, get_db

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create tables
from .models import room, booking, user, history

room.Base.metadata.create_all(bind=engine)
booking.Base.metadata.create_all(bind=engine)
user.Base.metadata.create_all(bind=engine)
history.Base.metadata.create_all(bind=engine)

# ПРОСТАЯ ПАРОЛЬНАЯ ЗАЩИТА
ADMIN_PASSWORD = "admin2024"  # ИЗМЕНИТЕ НА СВОЙ ПАРОЛЬ!
ACTIVE_TOKENS = {}  # Хранилище активных токенов


def generate_token():
    """Генерация случайного токена"""
    return secrets.token_urlsafe(32)


def verify_token(authorization: Optional[str] = Header(None)):
    """Проверка токена для защищенных операций"""
    if not authorization or not authorization.startswith("Bearer "):
        return None

    token = authorization.replace("Bearer ", "")
    if token in ACTIVE_TOKENS:
        # Обновляем время последней активности
        ACTIVE_TOKENS[token]["last_activity"] = datetime.now()
        return ACTIVE_TOKENS[token]
    return None


def require_auth(authorization: Optional[str] = Header(None)):
    """Требовать авторизацию для операции"""
    user_info = verify_token(authorization)
    if not user_info:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user_info


# Pydantic модели
class BookingCreate(BaseModel):
    room_id: int
    start_date: date
    end_date: date
    guest_name: Optional[str] = ""
    notes: Optional[str] = ""


class BookingUpdate(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    guest_name: Optional[str] = None
    notes: Optional[str] = None


class LoginRequest(BaseModel):
    password: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting application...")
    yield
    logger.info("Shutting down...")


app = FastAPI(
    title="Oqtoshsoy Resort Management API",
    version="2.0.0",
    description="Advanced hotel management system",
    lifespan=lifespan,
    redirect_slashes=False
)

# CORS настройка
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]
)

# Создаем роутеры для API
rooms_router = APIRouter(prefix="/api/rooms", tags=["rooms"])
bookings_router = APIRouter(prefix="/api/bookings", tags=["bookings"])


# ЭНДПОИНТ ДЛЯ ВХОДА
@app.post("/api/auth/login")
async def login(request: LoginRequest):
    """Простая авторизация по паролю"""
    if request.password != ADMIN_PASSWORD:
        logger.warning(f"Failed login attempt with password: {request.password[:3]}...")
        raise HTTPException(status_code=401, detail="Invalid password")

    # Генерируем токен
    token = generate_token()
    ACTIVE_TOKENS[token] = {
        "login_time": datetime.now(),
        "last_activity": datetime.now()
    }

    logger.info("Successful login")

    return {
        "token": token,
        "user": {
            "id": 1,
            "name": "Admin",
            "is_admin": True
        }
    }


# ПРОВЕРКА СТАТУСА АВТОРИЗАЦИИ
@app.get("/api/auth/check")
async def check_auth(authorization: Optional[str] = Header(None)):
    """Проверка текущей авторизации"""
    user_info = verify_token(authorization)
    return {
        "authenticated": user_info is not None,
        "user": {"name": "Admin", "is_admin": True} if user_info else None
    }


@rooms_router.get("")
@rooms_router.get("/")
async def get_rooms(
        room_type: Optional[str] = None,
        status: Optional[str] = None,
        db: Session = Depends(get_db)
        # БЕЗ АВТОРИЗАЦИИ - просмотр доступен всем
):
    """Получить все комнаты с фильтрами"""
    try:
        from sqlalchemy import text

        base_query = """
                     SELECT r.id,
                            r.room_number,
                            r.room_type,
                            COALESCE(r.capacity, 2)             as capacity,
                            COALESCE(r.price_per_night, 500000) as price_per_night,
                            COALESCE(r.description, '')         as description,
                            COALESCE(r.amenities, '')           as amenities,
                            r.created_at,
                            r.updated_at
                     FROM rooms r \
                     """

        conditions = []
        params = {}

        if room_type:
            conditions.append("r.room_type = :room_type")
            params['room_type'] = room_type

        if conditions:
            base_query += " WHERE " + " AND ".join(conditions)

        base_query += " ORDER BY r.id"

        result = db.execute(text(base_query), params)
        all_rooms = result.fetchall()

        type_map = {
            'STANDARD_2': "2 o'rinli standart",
            'STANDARD_4': "4 o'rinli standart",
            'LUX_2': "2 o'rinli lyuks",
            'VIP_SMALL_4': "4 o'rinli kichik VIP",
            'VIP_BIG_4': "4 o'rinli katta VIP",
            'APARTMENT_4': "4 o'rinli apartament",
            'COTTAGE_6': "Kottedj (6 kishi uchun)",
            'PRESIDENT_8': "Prezident apartamenti (8 kishi uchun)"
        }

        today = date.today()
        logger.info(f"Checking room availability for date: {today}")

        current_bookings_query = """
                                 SELECT b.room_id, b.id as booking_id, b.guest_name, b.start_date, b.end_date
                                 FROM bookings b
                                 WHERE b.start_date <= :today \
                                   AND b.end_date > :today \
                                 """

        current_bookings_result = db.execute(text(current_bookings_query), {"today": today})

        occupied_room_ids = set()
        bookings_dict = {}

        for booking in current_bookings_result:
            room_id = booking.room_id
            occupied_room_ids.add(room_id)
            bookings_dict[room_id] = {
                "id": booking.booking_id,
                "guest_name": booking.guest_name,
                "start_date": str(booking.start_date),
                "end_date": str(booking.end_date)
            }

        logger.info(f"Total occupied rooms: {len(occupied_room_ids)}")

        rooms = []
        for row in all_rooms:
            room_id = row.id
            room_type_display = type_map.get(row.room_type, row.room_type)

            is_available = room_id not in occupied_room_ids
            current_booking = bookings_dict.get(room_id, None)

            if status:
                if status == "available" and not is_available:
                    continue
                elif status == "occupied" and is_available:
                    continue

            rooms.append({
                "id": room_id,
                "room_number": row.room_number,
                "room_type": room_type_display,
                "capacity": row.capacity,
                "price_per_night": float(row.price_per_night),
                "description": row.description,
                "amenities": row.amenities,
                "created_at": row.created_at.isoformat() if row.created_at else "2024-01-01T00:00:00",
                "updated_at": row.updated_at.isoformat() if row.updated_at else "2024-01-01T00:00:00",
                "is_available": is_available,
                "current_booking": current_booking
            })

        logger.info(f"Returning {len(rooms)} rooms")
        return rooms

    except Exception as e:
        logger.error(f"Error in get_rooms: {e}")
        import traceback
        traceback.print_exc()
        return []


@rooms_router.get("/{room_id}")
async def get_room(room_id: int, db: Session = Depends(get_db)):
    """Получить комнату по ID"""
    try:
        from sqlalchemy import text

        result = db.execute(text("""
                                 SELECT *
                                 FROM rooms
                                 WHERE id = :id
                                 """), {"id": room_id})

        room = result.fetchone()
        if not room:
            raise HTTPException(status_code=404, detail="Room not found")

        type_map = {
            'STANDARD_2': "2 o'rinli standart",
            'STANDARD_4': "4 o'rinli standart",
            'LUX_2': "2 o'rinli lyuks",
            'VIP_SMALL_4': "4 o'rinli kichik VIP",
            'VIP_BIG_4': "4 o'rinli katta VIP",
            'APARTMENT_4': "4 o'rinli apartament",
            'COTTAGE_6': "Kottedj (6 kishi uchun)",
            'PRESIDENT_8': "Prezident apartamenti (8 kishi uchun)"
        }

        today = date.today()
        booking_check = db.execute(text("""
                                        SELECT COUNT(*)
                                        FROM bookings
                                        WHERE room_id = :room_id
                                          AND start_date <= :today
                                          AND end_date > :today
                                        """), {"room_id": room_id, "today": today})

        is_available = booking_check.scalar() == 0

        return {
            "id": room.id,
            "room_number": room.room_number,
            "room_type": type_map.get(room.room_type, room.room_type),
            "capacity": room.capacity or 2,
            "price_per_night": float(room.price_per_night) if room.price_per_night else 500000,
            "description": room.description or "",
            "amenities": room.amenities or "",
            "is_available": is_available
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_room: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@bookings_router.get("")
@bookings_router.get("/")
async def get_bookings(
        room_id: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        db: Session = Depends(get_db)
        # БЕЗ АВТОРИЗАЦИИ - просмотр доступен всем
):
    """Получить все бронирования с возможностью фильтрации"""
    try:
        from sqlalchemy import text

        query = """
                SELECT b.id,
                       b.room_id,
                       b.start_date,
                       b.end_date,
                       b.guest_name,
                       b.notes,
                       b.created_by,
                       b.created_at,
                       b.updated_at,
                       r.room_number,
                       r.room_type
                FROM bookings b
                         LEFT JOIN rooms r ON b.room_id = r.id \
                """

        conditions = []
        params = {}

        if room_id:
            conditions.append("b.room_id = :room_id")
            params['room_id'] = room_id

        if start_date:
            conditions.append("b.end_date >= :start_date")
            params['start_date'] = start_date

        if end_date:
            conditions.append("b.start_date <= :end_date")
            params['end_date'] = end_date

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY b.start_date DESC"

        result = db.execute(text(query), params)

        type_map = {
            'STANDARD_2': "2 o'rinli standart",
            'STANDARD_4': "4 o'rinli standart",
            'LUX_2': "2 o'rinli lyuks",
            'VIP_SMALL_4': "4 o'rinli kichik VIP",
            'VIP_BIG_4': "4 o'rinli katta VIP",
            'APARTMENT_4': "4 o'rinli apartament",
            'COTTAGE_6': "Kottedj (6 kishi uchun)",
            'PRESIDENT_8': "Prezident apartamenti (8 kishi uchun)"
        }

        bookings = []
        for row in result:
            bookings.append({
                "id": row.id,
                "room_id": row.room_id,
                "start_date": str(row.start_date) if row.start_date else None,
                "end_date": str(row.end_date) if row.end_date else None,
                "guest_name": row.guest_name or "",
                "notes": row.notes or "",
                "created_by": row.created_by or 1,
                "created_at": row.created_at.isoformat() if row.created_at else "2024-01-01T00:00:00",
                "updated_at": row.updated_at.isoformat() if row.updated_at else "2024-01-01T00:00:00",
                "room": {
                    "id": row.room_id,
                    "room_number": row.room_number,
                    "room_type": type_map.get(row.room_type, row.room_type)
                } if row.room_number else None
            })

        logger.info(f"Returning {len(bookings)} bookings")
        return bookings

    except Exception as e:
        logger.error(f"Error in get_bookings: {e}")
        return []


@bookings_router.post("/v2")
@bookings_router.post("")
@bookings_router.post("/")
async def create_booking(
        booking_data: BookingCreate,
        db: Session = Depends(get_db),
        user_info=Depends(require_auth)  # ТРЕБУЕТ АВТОРИЗАЦИЮ
):
    """Создать новое бронирование"""
    try:
        from sqlalchemy import text

        logger.info(f"Admin creating booking for room {booking_data.room_id}")

        room_check = db.execute(text("""
                                     SELECT id, room_number
                                     FROM rooms
                                     WHERE id = :room_id
                                     """), {"room_id": booking_data.room_id})

        room = room_check.fetchone()
        if not room:
            raise HTTPException(status_code=404, detail=f"Room with ID {booking_data.room_id} not found")

        conflicts = db.execute(text("""
                                    SELECT id, start_date, end_date, guest_name
                                    FROM bookings
                                    WHERE room_id = :room_id
                                      AND start_date < :end_date
                                      AND end_date > :start_date
                                    """), {
                                   "room_id": booking_data.room_id,
                                   "start_date": booking_data.start_date,
                                   "end_date": booking_data.end_date
                               })

        conflict_list = conflicts.fetchall()
        if conflict_list:
            conflict_details = []
            for c in conflict_list:
                conflict_details.append(f"{c.start_date} - {c.end_date}")

            error_message = f"Room #{room.room_number} is not available. Conflicts: {'; '.join(conflict_details)}"
            logger.warning(error_message)
            raise HTTPException(status_code=400, detail=error_message)

        result = db.execute(text("""
                                 INSERT INTO bookings (room_id, start_date, end_date, guest_name, notes, created_by,
                                                       created_at, updated_at)
                                 VALUES (:room_id, :start_date, :end_date, :guest_name, :notes, :created_by, NOW(),
                                         NOW()) RETURNING id
                                 """), {
                                "room_id": booking_data.room_id,
                                "start_date": booking_data.start_date,
                                "end_date": booking_data.end_date,
                                "guest_name": booking_data.guest_name,
                                "notes": booking_data.notes,
                                "created_by": 1
                            })

        booking_id = result.scalar()
        db.commit()

        logger.info(f"Successfully created booking #{booking_id} for room #{room.room_number}")

        booking = db.execute(text("""
                                  SELECT b.*, r.room_number, r.room_type
                                  FROM bookings b
                                           LEFT JOIN rooms r ON b.room_id = r.id
                                  WHERE b.id = :id
                                  """), {"id": booking_id}).fetchone()

        type_map = {
            'STANDARD_2': "2 o'rinli standart",
            'STANDARD_4': "4 o'rinli standart",
            'LUX_2': "2 o'rinli lyuks",
            'VIP_SMALL_4': "4 o'rinli kichik VIP",
            'VIP_BIG_4': "4 o'rinli katta VIP",
            'APARTMENT_4': "4 o'rinli apartament",
            'COTTAGE_6': "Kottedj (6 kishi uchun)",
            'PRESIDENT_8': "Prezident apartamenti (8 kishi uchun)"
        }

        return {
            "id": booking.id,
            "room_id": booking.room_id,
            "start_date": str(booking.start_date),
            "end_date": str(booking.end_date),
            "guest_name": booking.guest_name,
            "notes": booking.notes,
            "created_by": booking.created_by,
            "created_at": booking.created_at.isoformat() if booking.created_at else None,
            "updated_at": booking.updated_at.isoformat() if booking.updated_at else None,
            "room": {
                "id": booking.room_id,
                "room_number": booking.room_number,
                "room_type": type_map.get(booking.room_type, booking.room_type)
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating booking: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@bookings_router.delete("/{booking_id}")
async def delete_booking(
        booking_id: int,
        db: Session = Depends(get_db),
        user_info=Depends(require_auth)  # ТРЕБУЕТ АВТОРИЗАЦИЮ
):
    """Удалить бронирование"""
    try:
        from sqlalchemy import text

        logger.info(f"Admin attempting to delete booking #{booking_id}")

        check = db.execute(text("SELECT id, room_id FROM bookings WHERE id = :id"), {"id": booking_id})
        booking = check.fetchone()
        if not booking:
            logger.warning(f"Booking {booking_id} not found")
            raise HTTPException(status_code=404, detail="Booking not found")

        db.execute(text("DELETE FROM bookings WHERE id = :id"), {"id": booking_id})
        db.commit()

        logger.info(f"Successfully deleted booking #{booking_id}")
        return {"message": "Booking deleted successfully", "id": booking_id}

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting booking {booking_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@bookings_router.put("/{booking_id}")
@bookings_router.patch("/{booking_id}")
async def update_booking(
        booking_id: int,
        booking_data: BookingUpdate,
        db: Session = Depends(get_db),
        user_info=Depends(require_auth)  # ТРЕБУЕТ АВТОРИЗАЦИЮ
):
    """Обновить бронирование"""
    try:
        from sqlalchemy import text

        check = db.execute(text("SELECT * FROM bookings WHERE id = :id"), {"id": booking_id})
        existing = check.fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail="Booking not found")

        check_start = booking_data.start_date if booking_data.start_date else existing.start_date
        check_end = booking_data.end_date if booking_data.end_date else existing.end_date

        if booking_data.start_date or booking_data.end_date:
            conflicts = db.execute(text("""
                                        SELECT COUNT(*)
                                        FROM bookings
                                        WHERE room_id = :room_id
                                          AND id != :booking_id
                  AND start_date < :end_date
                  AND end_date > :start_date
                                        """), {
                                       "room_id": existing.room_id,
                                       "booking_id": booking_id,
                                       "start_date": check_start,
                                       "end_date": check_end
                                   })

            if conflicts.scalar() > 0:
                raise HTTPException(status_code=400, detail="Room is not available for selected dates")

        updates = []
        params = {"id": booking_id}

        if booking_data.start_date is not None:
            updates.append("start_date = :start_date")
            params["start_date"] = booking_data.start_date

        if booking_data.end_date is not None:
            updates.append("end_date = :end_date")
            params["end_date"] = booking_data.end_date

        if booking_data.guest_name is not None:
            updates.append("guest_name = :guest_name")
            params["guest_name"] = booking_data.guest_name

        if booking_data.notes is not None:
            updates.append("notes = :notes")
            params["notes"] = booking_data.notes

        if updates:
            updates.append("updated_at = NOW()")
            query = f"UPDATE bookings SET {', '.join(updates)} WHERE id = :id"
            db.execute(text(query), params)
            db.commit()

        booking = db.execute(text("""
                                  SELECT b.*, r.room_number, r.room_type
                                  FROM bookings b
                                           LEFT JOIN rooms r ON b.room_id = r.id
                                  WHERE b.id = :id
                                  """), {"id": booking_id}).fetchone()

        type_map = {
            'STANDARD_2': "2 o'rinli standart",
            'STANDARD_4': "4 o'rinli standart",
            'LUX_2': "2 o'rinli lyuks",
            'VIP_SMALL_4': "4 o'rinli kichik VIP",
            'VIP_BIG_4': "4 o'rinli katta VIP",
            'APARTMENT_4': "4 o'rinli apartament",
            'COTTAGE_6': "Kottedj (6 kishi uchun)",
            'PRESIDENT_8': "Prezident apartamenti (8 kushi uchun)"
        }

        return {
            "id": booking.id,
            "room_id": booking.room_id,
            "start_date": str(booking.start_date),
            "end_date": str(booking.end_date),
            "guest_name": booking.guest_name,
            "notes": booking.notes,
            "created_by": booking.created_by,
            "created_at": booking.created_at.isoformat() if booking.created_at else None,
            "updated_at": booking.updated_at.isoformat() if booking.updated_at else None,
            "room": {
                "id": booking.room_id,
                "room_number": booking.room_number,
                "room_type": type_map.get(booking.room_type, booking.room_type)
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating booking: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Регистрируем роутеры
app.include_router(rooms_router)
app.include_router(bookings_router)


# Дополнительные эндпоинты
@app.get("/api/analytics")
async def analytics_placeholder():
    return {"message": "Analytics module is under development"}


@app.get("/api/export")
async def export_placeholder():
    return {"message": "Export module is under development"}


@app.get("/api/history")
async def history_placeholder():
    return {"message": "History module is under development"}


@app.get("/")
async def root():
    return {
        "message": "Oqtoshsoy Resort Management System API",
        "version": "2.0.0",
        "status": "active"
    }


@app.get("/api")
async def api_root():
    return {"message": "API is running", "version": "2.0.0"}


# Отладочный эндпоинт
@app.get("/api/debug/room-status")
async def debug_room_status(db: Session = Depends(get_db)):
    """Отладочный эндпоинт для проверки статуса комнат"""
    try:
        from sqlalchemy import text

        rooms = db.execute(text("SELECT id, room_number, room_type FROM rooms ORDER BY id")).fetchall()

        today = date.today()
        active_bookings = db.execute(text("""
                                          SELECT room_id, id as booking_id, guest_name, start_date, end_date
                                          FROM bookings
                                          WHERE start_date <= :today
                                            AND end_date > :today
                                          """), {"today": today}).fetchall()

        occupied = {}
        for booking in active_bookings:
            occupied[booking.room_id] = {
                "booking_id": booking.booking_id,
                "guest": booking.guest_name,
                "dates": f"{booking.start_date} to {booking.end_date}"
            }

        result = []
        for room in rooms:
            result.append({
                "room_id": room.id,
                "room_number": room.room_number,
                "room_type": room.room_type,
                "is_available": room.id not in occupied,
                "booking": occupied.get(room.id)
            })

        return {
            "date": str(today),
            "total_rooms": len(rooms),
            "occupied_rooms": len(occupied),
            "available_rooms": len(rooms) - len(occupied),
            "rooms": result
        }

    except Exception as e:
        logger.error(f"Error in debug_room_status: {e}")
        return {"error": str(e)}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)