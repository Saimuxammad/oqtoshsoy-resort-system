# backend/app/fix_room_types.py
# Скрипт для исправления типов комнат в БД

from sqlalchemy import create_engine, text
import os


def fix_room_types():
    """Конвертирует enum типы в строки в PostgreSQL"""

    # Получаем URL базы данных
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./oqtoshsoy_resort.db")
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

    engine = create_engine(DATABASE_URL)

    with engine.connect() as conn:
        try:
            # 1. Сначала добавляем временную колонку
            print("Adding temporary column...")
            conn.execute(text("""
                              ALTER TABLE rooms
                                  ADD COLUMN IF NOT EXISTS room_type_temp VARCHAR (100)
                              """))
            conn.commit()

            # 2. Копируем данные из enum в строку
            print("Copying data from enum to string...")
            conn.execute(text("""
                              UPDATE rooms
                              SET room_type_temp = room_type::text
                              """))
            conn.commit()

            # 3. Удаляем старую колонку
            print("Dropping old column...")
            conn.execute(text("""
                              ALTER TABLE rooms
                              DROP
                              COLUMN room_type
                              """))
            conn.commit()

            # 4. Переименовываем новую колонку
            print("Renaming column...")
            conn.execute(text("""
                              ALTER TABLE rooms
                                  RENAME COLUMN room_type_temp TO room_type
                              """))
            conn.commit()

            # 5. Удаляем старый enum тип если существует
            print("Dropping old enum type...")
            conn.execute(text("""
                DROP TYPE IF EXISTS roomtype CASCADE
            """))
            conn.commit()

            # 6. Обновляем значения на человекочитаемые
            print("Updating room type values...")
            room_type_map = {
                'STANDARD_DOUBLE': "2 o'rinli standart",
                'STANDARD_QUAD': "4 o'rinli standart",
                'LUX_DOUBLE': "2 o'rinli lyuks",
                'VIP_SMALL': "4 o'rinli kichik VIP",
                'VIP_LARGE': "4 o'rinli katta VIP",
                'APARTMENT': "4 o'rinli apartament",
                'COTTAGE': "Kottedj (6 kishi uchun)",
                'PRESIDENT': "Prezident apartamenti (8 kishi uchun)"
            }

            for old_value, new_value in room_type_map.items():
                conn.execute(
                    text("UPDATE rooms SET room_type = :new_value WHERE room_type = :old_value"),
                    {"old_value": old_value, "new_value": new_value}
                )
            conn.commit()

            # 7. Проверяем результат
            result = conn.execute(text("SELECT COUNT(*), room_type FROM rooms GROUP BY room_type"))
            print("\nRoom types after migration:")
            for row in result:
                print(f"  {row[1]}: {row[0]} rooms")

            print("\nMigration completed successfully!")

        except Exception as e:
            print(f"Error during migration: {e}")
            conn.rollback()
            raise


if __name__ == "__main__":
    fix_room_types()