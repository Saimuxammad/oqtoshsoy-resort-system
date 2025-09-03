from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
import uvicorn
from datetime import datetime, date
import logging
import os
from typing import Optional

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


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting application...")
    yield
    # Shutdown
    logger.info("Shutting down...")


app = FastAPI(
    title="Oqtoshsoy Resort Management API",
    version="2.0.0",
    description="Advanced hotel management system",
    lifespan=lifespan,
    redirect_slashes=False
)

# CORS настройка
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
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


@app.get("/api/test")
async def test_endpoint():
    return {"status": "ok", "message": "API is working"}


# КРИТИЧЕСКИ ВАЖНЫЙ ЭНДПОИНТ - конвертирует enum в varchar
@app.get("/api/convert-enum-to-string")
async def convert_enum_to_string(db: Session = Depends(get_db)):
    """Конвертирует enum тип в обычную строку в PostgreSQL"""
    try:
        from sqlalchemy import text

        # 1. Создаем временную колонку
        logger.info("Step 1: Creating temporary column...")
        db.execute(text("ALTER TABLE rooms ADD COLUMN IF NOT EXISTS room_type_new VARCHAR(100)"))
        db.commit()

        # 2. Копируем данные из enum в строку с преобразованием
        logger.info("Step 2: Copying and converting data...")
        db.execute(text("""
            UPDATE rooms 
            SET room_type_new = CASE 
                WHEN room_type::text = 'STANDARD_DOUBLE' THEN '2 o''rinli standart'
                WHEN room_type::text = 'STANDARD_QUAD' THEN '4 o''rinli standart'
                WHEN room_type::text = 'LUX_DOUBLE' THEN '2 o''rinli lyuks'
                WHEN room_type::text = 'VIP_SMALL' THEN '4 o''rinli kichik VIP'
                WHEN room_type::text = 'VIP_LARGE' THEN '4 o''rinli katta VIP'
                WHEN room_type::text = 'APARTMENT' THEN '4 o''rinli apartament'
                WHEN room_type::text = 'COTTAGE' THEN 'Kottedj (6 kishi uchun)'
                WHEN room_type::text = 'PRESIDENT' THEN 'Prezident apartamenti (8 kishi uchun)'
                ELSE room_type::text
            END
        """))
        db.commit()

        # 3. Удаляем старую колонку
        logger.info("Step 3: Dropping old column...")
        db.execute(text("ALTER TABLE rooms DROP COLUMN room_type"))
        db.commit()

        # 4. Переименовываем новую колонку
        logger.info("Step 4: Renaming column...")
        db.execute(text("ALTER TABLE rooms RENAME COLUMN room_type_new TO room_type"))
        db.commit()

        # 5. Пытаемся удалить старый enum тип
        logger.info("Step 5: Attempting to drop old enum type...")
        try:
            db.execute(text("DROP TYPE IF EXISTS roomtype CASCADE"))
            db.commit()
        except:
            pass  # Игнорируем если не получается удалить

        # 6. Проверяем результат
        result = db.execute(text("SELECT COUNT(*), room_type FROM rooms GROUP BY room_type"))
        stats = []
        for row in result:
            stats.append(f"{row[1]}: {row[0]} rooms")

        return {
            "status": "success",
            "message": "Enum successfully converted to string",
            "room_types": stats
        }

    except Exception as e:
        db.rollback()
        logger.error(f"Error converting enum: {e}")
        return {"status": "error", "message": str(e)}


# API для комнат - работает напрямую с SQL для избежания проблем с ORM
@app.get("/api/rooms")
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
            SELECT 
                r.id,
                r.room_number,
                r.room_type::text as room_type,
                COALESCE(r.capacity, 2) as capacity,
                COALESCE(r.price_per_night, 500000) as price_per_night,
                COALESCE(r.description, '') as description,
                COALESCE(r.amenities, '') as amenities,
                r.created_at,
                r.updated_at
            FROM rooms r
        """

        # Добавляем фильтры
        conditions = []
        params = {}

        if room_type:
            # Для фильтра по типу используем LIKE для обхода enum
            conditions.append("r.room_type::text LIKE :room_type")
            # Маппинг для обратной совместимости
            if room_type == "2 o'rinli standart":
                params['room_type'] = '%STANDARD_DOUBLE%'
            elif room_type == "4 o'rinli standart":
                params['room_type'] = '%STANDARD_QUAD%'
            elif room_type == "2 o'rinli lyuks":
                params['room_type'] = '%LUX%'
            elif room_type == "4 o'rinli kichik VIP":
                params['room_type'] = '%VIP_SMALL%'
            elif room_type == "4 o'rinli katta VIP":
                params['room_type'] = '%VIP_LARGE%'
            elif room_type == "4 o'rinli apartament":
                params['room_type'] = '%APARTMENT%'
            elif room_type == "Kottedj (6 kishi uchun)":
                params['room_type'] = '%COTTAGE%'
            elif room_type == "Prezident apartamenti (8 kishi uchun)":
                params['room_type'] = '%PRESIDENT%'
            else:
                params['room_type'] = f'%{room_type}%'

        if conditions:
            base_query += " WHERE " + " AND ".join(conditions)

        base_query += " ORDER BY r.id"

        # Выполняем запрос
        result = db.execute(text(base_query), params)

        rooms = []
        for row in result:
            # Преобразуем enum значения в человекочитаемые
            room_type_display = row.room_type
            if 'STANDARD_DOUBLE' in str(room_type_display):
                room_type_display = "2 o'rinli standart"
            elif 'STANDARD_QUAD' in str(room_type_display):
                room_type_display = "4 o'rinli standart"
            elif 'LUX_DOUBLE' in str(room_type_display) or 'LUX' in str(room_type_display):
                room_type_display = "2 o'rinli lyuks"
            elif 'VIP_SMALL' in str(room_type_display):
                room_type_display = "4 o'rinli kichik VIP"
            elif 'VIP_LARGE' in str(room_type_display):
                room_type_display = "4 o'rinli katta VIP"
            elif 'APARTMENT' in str(room_type_display):
                room_type_display = "4 o'rinli apartament"
            elif 'COTTAGE' in str(room_type_display):
                room_type_display = "Kottedj (6 kishi uchun)"
            elif 'PRESIDENT' in str(room_type_display):
                room_type_display = "Prezident apartamenti (8 kishi uchun)"

            # Проверяем занятость если нужен фильтр по статусу
            is_available = True
            if status:
                booking_check = db.execute(text("""
                    SELECT COUNT(*) FROM bookings 
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

        return rooms

    except Exception as e:
        logger.error(f"Error in get_rooms: {e}")
        import traceback
        traceback.print_exc()
        return []


# API для бронирований
@app.get("/api/bookings")
async def get_bookings(
    current_user: Optional[str] = "user",  # Временный обход авторизации
    db: Session = Depends(get_db)
):
    """Получить все бронирования"""
    try:
        from sqlalchemy import text

        result = db.execute(text("""
            SELECT 
                b.id,
                b.room_id,
                b.start_date,
                b.end_date,
                b.guest_name,
                b.notes,
                b.created_by,
                b.created_at,
                b.updated_at,
                r.room_number,
                r.room_type::text as room_type
            FROM bookings b
            LEFT JOIN rooms r ON b.room_id = r.id
            ORDER BY b.start_date DESC
        """))

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
                    "room_type": row.room_type
                } if row.room_number else None
            })

        return bookings

    except Exception as e:
        logger.error(f"Error in get_bookings: {e}")
        return []


# Создание бронирования
@app.post("/api/bookings")
async def create_booking(
    booking_data: dict,
    current_user: Optional[str] = "user",  # Временный обход
    db: Session = Depends(get_db)
):
    """Создать новое бронирование"""
    try:
        from sqlalchemy import text

        # Проверяем доступность
        check = db.execute(text("""
            SELECT COUNT(*) FROM bookings 
            WHERE room_id = :room_id 
            AND start_date <= :end_date 
            AND end_date >= :start_date
        """), {
            "room_id": booking_data["room_id"],
            "start_date": booking_data["start_date"],
            "end_date": booking_data["end_date"]
        })

        if check.scalar() > 0:
            raise HTTPException(status_code=400, detail="Room is not available for selected dates")

        # Создаем бронирование
        result = db.execute(text("""
            INSERT INTO bookings (room_id, start_date, end_date, guest_name, notes, created_by, created_at, updated_at)
            VALUES (:room_id, :start_date, :end_date, :guest_name, :notes, :created_by, NOW(), NOW())
            RETURNING id
        """), {
            "room_id": booking_data["room_id"],
            "start_date": booking_data["start_date"],
            "end_date": booking_data["end_date"],
            "guest_name": booking_data.get("guest_name", ""),
            "notes": booking_data.get("notes", ""),
            "created_by": 1  # Временно хардкодим
        })

        booking_id = result.scalar()
        db.commit()

        # Возвращаем созданное бронирование
        booking = db.execute(text("""
            SELECT 
                b.*,
                r.room_number,
                r.room_type::text as room_type
            FROM bookings b
            LEFT JOIN rooms r ON b.room_id = r.id
            WHERE b.id = :id
        """), {"id": booking_id}).fetchone()

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
                "room_type": booking.room_type
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating booking: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Удаление бронирования
@app.delete("/api/bookings/{booking_id}")
async def delete_booking(
    booking_id: int,
    current_user: Optional[str] = "user",  # Временный обход
    db: Session = Depends(get_db)
):
    """Удалить бронирование"""
    try:
        from sqlalchemy import text

        # Проверяем существование
        check = db.execute(text("SELECT id FROM bookings WHERE id = :id"), {"id": booking_id})
        if not check.fetchone():
            raise HTTPException(status_code=404, detail="Booking not found")

        # Удаляем
        db.execute(text("DELETE FROM bookings WHERE id = :id"), {"id": booking_id})
        db.commit()

        return {"message": "Booking deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting booking: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Обновление бронирования
@app.put("/api/bookings/{booking_id}")
@app.patch("/api/bookings/{booking_id}")
async def update_booking(
    booking_id: int,
    booking_data: dict,
    current_user: Optional[str] = "user",
    db: Session = Depends(get_db)
):
    """Обновить бронирование"""
    try:
        from sqlalchemy import text

        # Проверяем существование
        check = db.execute(text("SELECT * FROM bookings WHERE id = :id"), {"id": booking_id})
        existing = check.fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail="Booking not found")

        # Обновляем только переданные поля
        updates = []
        params = {"id": booking_id}

        if "start_date" in booking_data:
            updates.append("start_date = :start_date")
            params["start_date"] = booking_data["start_date"]

        if "end_date" in booking_data:
            updates.append("end_date = :end_date")
            params["end_date"] = booking_data["end_date"]

        if "guest_name" in booking_data:
            updates.append("guest_name = :guest_name")
            params["guest_name"] = booking_data["guest_name"]

        if "notes" in booking_data:
            updates.append("notes = :notes")
            params["notes"] = booking_data["notes"]

        if updates:
            updates.append("updated_at = NOW()")
            query = f"UPDATE bookings SET {', '.join(updates)} WHERE id = :id"
            db.execute(text(query), params)
            db.commit()

        # Возвращаем обновленное бронирование
        booking = db.execute(text("""
            SELECT 
                b.*,
                r.room_number,
                r.room_type::text as room_type
            FROM bookings b
            LEFT JOIN rooms r ON b.room_id = r.id
            WHERE b.id = :id
        """), {"id": booking_id}).fetchone()

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
                "room_type": booking.room_type
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating booking: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)