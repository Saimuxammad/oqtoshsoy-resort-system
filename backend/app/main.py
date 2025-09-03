from fastapi import FastAPI, HTTPException, Depends, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
import uvicorn
from datetime import datetime, date
import logging
import os
from typing import Optional, List
from pydantic import BaseModel

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


@rooms_router.get("")
@rooms_router.get("/")
async def get_rooms(
        room_type: Optional[str] = None,
        status: Optional[str] = None,
        db: Session = Depends(get_db)
):
    """Получить все комнаты с фильтрами"""
    try:
        from sqlalchemy import text

        # Базовый SQL запрос
        base_query = """
                     SELECT r.id, \
                            r.room_number, \
                            r.room_type, \
                            COALESCE(r.capacity, 2)             as capacity, \
                            COALESCE(r.price_per_night, 500000) as price_per_night, \
                            COALESCE(r.description, '')         as description, \
                            COALESCE(r.amenities, '')           as amenities, \
                            r.created_at, \
                            r.updated_at
                     FROM rooms r \
                     """

        # Добавляем фильтры
        conditions = []
        params = {}

        if room_type:
            conditions.append("r.room_type = :room_type")
            params['room_type'] = room_type

        if conditions:
            base_query += " WHERE " + " AND ".join(conditions)

        base_query += " ORDER BY r.id"

        # Выполняем запрос
        result = db.execute(text(base_query), params)

        rooms = []
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

        for row in result:
            # Проверяем и конвертируем тип комнаты
            room_type_display = type_map.get(row.room_type, row.room_type)

            # Проверяем занятость если нужен фильтр по статусу
            is_available = True
            if status:
                # Используем <= и >= для текущей даты, так как гость еще находится в номере
                booking_check = db.execute(text("""
                                                SELECT COUNT(*)
                                                FROM bookings
                                                WHERE room_id = :room_id
                                                  AND start_date <= :today
                                                  AND end_date >= :today
                                                """), {"room_id": row.id, "today": date.today()})
                is_occupied = booking_check.scalar() > 0

                if status == "available" and is_occupied:
                    continue
                elif status == "occupied" and not is_occupied:
                    continue

                is_available = not is_occupied

            rooms.append({
                "id": row.id,
                "room_number": row.room_number,
                "room_type": room_type_display,
                "capacity": row.capacity,
                "price_per_night": float(row.price_per_night),
                "description": row.description,
                "amenities": row.amenities,
                "created_at": row.created_at.isoformat() if row.created_at else "2024-01-01T00:00:00",
                "updated_at": row.updated_at.isoformat() if row.updated_at else "2024-01-01T00:00:00",
                "is_available": is_available,
                "current_booking": None
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

        return {
            "id": room.id,
            "room_number": room.room_number,
            "room_type": type_map.get(room.room_type, room.room_type),
            "capacity": room.capacity or 2,
            "price_per_night": float(room.price_per_night) if room.price_per_night else 500000,
            "description": room.description or "",
            "amenities": room.amenities or "",
            "is_available": True
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_room: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@bookings_router.get("")
@bookings_router.get("/")
async def get_bookings(db: Session = Depends(get_db)):
    """Получить все бронирования"""
    try:
        from sqlalchemy import text

        result = db.execute(text("""
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
                                          LEFT JOIN rooms r ON b.room_id = r.id
                                 ORDER BY b.start_date DESC
                                 """))

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

        return bookings

    except Exception as e:
        logger.error(f"Error in get_bookings: {e}")
        return []


@bookings_router.post("")
@bookings_router.post("/")
async def create_booking(booking_data: BookingCreate, db: Session = Depends(get_db)):
    """Создать новое бронирование"""
    try:
        from sqlalchemy import text

        # Проверяем доступность
        check = db.execute(text("""
                                SELECT COUNT(*)
                                FROM bookings
                                WHERE room_id = :room_id
                                  AND start_date <= :end_date
                                  AND end_date >= :start_date
                                """), {
                               "room_id": booking_data.room_id,
                               "start_date": booking_data.start_date,
                               "end_date": booking_data.end_date
                           })

        if check.scalar() > 0:
            raise HTTPException(status_code=400, detail="Room is not available for selected dates")

        # Создаем бронирование
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

        # Возвращаем созданное бронирование
        booking = db.execute(text("""
                                  SELECT b.*,
                                         r.room_number,
                                         r.room_type
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
async def delete_booking(booking_id: int, db: Session = Depends(get_db)):
    """Удалить бронирование"""
    try:
        from sqlalchemy import text

        # Логируем для отладки
        logger.info(f"Attempting to delete booking with id: {booking_id}")

        check = db.execute(text("SELECT id FROM bookings WHERE id = :id"), {"id": booking_id})
        booking = check.fetchone()
        if not booking:
            logger.warning(f"Booking {booking_id} not found")
            raise HTTPException(status_code=404, detail="Booking not found")

        db.execute(text("DELETE FROM bookings WHERE id = :id"), {"id": booking_id})
        db.commit()

        logger.info(f"Successfully deleted booking {booking_id}")
        return {"message": "Booking deleted successfully", "id": booking_id}

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting booking {booking_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@bookings_router.put("/{booking_id}")
@bookings_router.patch("/{booking_id}")
async def update_booking(booking_id: int, booking_data: BookingUpdate, db: Session = Depends(get_db)):
    """Обновить бронирование"""
    try:
        from sqlalchemy import text

        check = db.execute(text("SELECT * FROM bookings WHERE id = :id"), {"id": booking_id})
        existing = check.fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail="Booking not found")

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
                                  SELECT b.*,
                                         r.room_number,
                                         r.room_type
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
        logger.error(f"Error updating booking: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Регистрируем роутеры
app.include_router(rooms_router)
app.include_router(bookings_router)


# Добавляем пустые роутеры для других разделов чтобы не было 404
@app.get("/api/analytics")
async def analytics_placeholder():
    return {"message": "Analytics module is under development"}


@app.get("/api/export")
async def export_placeholder():
    return {"message": "Export module is under development"}


@app.get("/api/history")
async def history_placeholder():
    return {"message": "History module is under development"}


@app.get("/api/auth/login")
async def auth_placeholder():
    return {"token": "dev_token", "user": {"id": 1, "name": "Test User"}}


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


@app.get("/api/fix-room-types")
async def fix_room_types(db: Session = Depends(get_db)):
    """Обновляет типы комнат на узбекские названия"""
    try:
        from sqlalchemy import text

        logger.info("Updating room types to Uzbek names...")

        updates = [
            ("STANDARD_2", "2 o'rinli standart"),
            ("STANDARD_4", "4 o'rinli standart"),
            ("LUX_2", "2 o'rinli lyuks"),
            ("VIP_SMALL_4", "4 o'rinli kichik VIP"),
            ("VIP_BIG_4", "4 o'rinli katta VIP"),
            ("APARTMENT_4", "4 o'rinli apartament"),
            ("COTTAGE_6", "Kottedj (6 kishi uchun)"),
            ("PRESIDENT_8", "Prezident apartamenti (8 kishi uchun)")
        ]

        total_updated = 0
        for old_type, new_type in updates:
            result = db.execute(text("""
                                     UPDATE rooms
                                     SET room_type = :new_type
                                     WHERE room_type = :old_type
                                     """), {"old_type": old_type, "new_type": new_type})
            total_updated += result.rowcount
            db.commit()

        # Проверяем результат
        result = db.execute(text("SELECT room_type, COUNT(*) FROM rooms GROUP BY room_type ORDER BY room_type"))
        room_types = []
        for row in result:
            room_types.append(f"{row[0]}: {row[1]} rooms")

        return {
            "status": "success",
            "message": f"Updated {total_updated} rooms",
            "current_types": room_types
        }

    except Exception as e:
        db.rollback()
        logger.error(f"Error updating room types: {e}")
        return {"status": "error", "message": str(e)}


@app.get("/api/test-booking-conflicts")
async def test_booking_conflicts(
        room_id: int,
        start_date: date,
        end_date: date,
        db: Session = Depends(get_db)
):
    """Тестовый эндпоинт для отладки конфликтов бронирования"""
    try:
        from sqlalchemy import text

        # Получаем все бронирования для этой комнаты
        all_bookings = db.execute(text("""
                                       SELECT id, room_id, start_date, end_date, guest_name
                                       FROM bookings
                                       WHERE room_id = :room_id
                                       ORDER BY start_date
                                       """), {"room_id": room_id})

        bookings_list = []
        for b in all_bookings:
            bookings_list.append({
                "id": b.id,
                "start_date": str(b.start_date),
                "end_date": str(b.end_date),
                "guest_name": b.guest_name
            })

        # Проверяем конфликты со старой логикой (<=, >=)
        old_conflicts = db.execute(text("""
                                        SELECT id, start_date, end_date
                                        FROM bookings
                                        WHERE room_id = :room_id
                                          AND start_date <= :end_date
                                          AND end_date >= :start_date
                                        """), {
                                       "room_id": room_id,
                                       "start_date": start_date,
                                       "end_date": end_date
                                   })

        old_conflicts_list = []
        for c in old_conflicts:
            old_conflicts_list.append({
                "id": c.id,
                "start_date": str(c.start_date),
                "end_date": str(c.end_date)
            })

        # Проверяем конфликты с новой логикой (<, >)
        new_conflicts = db.execute(text("""
                                        SELECT id, start_date, end_date
                                        FROM bookings
                                        WHERE room_id = :room_id
                                          AND start_date < :end_date
                                          AND end_date > :start_date
                                        """), {
                                       "room_id": room_id,
                                       "start_date": start_date,
                                       "end_date": end_date
                                   })

        new_conflicts_list = []
        for c in new_conflicts:
            new_conflicts_list.append({
                "id": c.id,
                "start_date": str(c.start_date),
                "end_date": str(c.end_date)
            })

        return {
            "requested_booking": {
                "room_id": room_id,
                "start_date": str(start_date),
                "end_date": str(end_date)
            },
            "existing_bookings": bookings_list,
            "old_logic_conflicts": old_conflicts_list,
            "new_logic_conflicts": new_conflicts_list,
            "old_logic_available": len(old_conflicts_list) == 0,
            "new_logic_available": len(new_conflicts_list) == 0,
            "recommendation": "Use new logic - allows same day checkout/checkin" if len(
                new_conflicts_list) == 0 else "Room not available"
        }

    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)