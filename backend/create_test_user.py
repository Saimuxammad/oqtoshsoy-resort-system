# backend/create_test_user.py
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.database import SessionLocal, engine
from backend.app.models import user, room, booking, history
from backend.app.models.user import User

# Создаем таблицы если их нет
user.Base.metadata.create_all(bind=engine)
room.Base.metadata.create_all(bind=engine)
booking.Base.metadata.create_all(bind=engine)
history.Base.metadata.create_all(bind=engine)

db = SessionLocal()

try:
    # Проверяем есть ли тестовый пользователь
    test_user = db.query(User).filter(User.telegram_id == 5488749868).first()

    if not test_user:
        # Создаем тестового пользователя
        test_user = User(
            telegram_id=5488749868,
            first_name="Test",
            last_name="User",
            username="testuser",
            is_admin=True,
            is_active=True
        )
        db.add(test_user)
        db.commit()
        print("✅ Test user created successfully!")
    else:
        print("ℹ️ Test user already exists")

    # Показываем всех пользователей
    users = db.query(User).all()
    print(f"\n👥 Users in database:")
    for user in users:
        print(f"  - {user.first_name} {user.last_name} (ID: {user.telegram_id}, Admin: {user.is_admin})")

finally:
    db.close()