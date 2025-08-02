import os
import httpx
from datetime import datetime, date
from typing import Optional
from sqlalchemy.orm import Session

from ..models.booking import Booking
from ..models.room import Room
from ..models.user import User


class NotificationService:
    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        self.web_app_url = os.getenv("WEB_APP_URL", "https://oqtoshsoy-resort-system-production-ef7c.up.railway.app")

    async def send_message(self, chat_id: int, text: str, parse_mode: str = "HTML"):
        """Send message via Telegram Bot API"""
        if not self.bot_token:
            print("Telegram bot token not configured")
            return

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/sendMessage",
                    json={
                        "chat_id": chat_id,
                        "text": text,
                        "parse_mode": parse_mode
                    }
                )
                if response.status_code != 200:
                    print(f"Failed to send message: {response.text}")
        except Exception as e:
            print(f"Error sending telegram message: {e}")

    async def send_booking_created(self, db: Session, booking: Booking, room: Room, user: User):
        """Send notification about new booking"""
        # Format dates
        start_date = booking.start_date.strftime("%d.%m.%Y")
        end_date = booking.end_date.strftime("%d.%m.%Y")

        text = (
            f"✅ <b>Yangi bron yaratildi</b>\n\n"
            f"🏠 Xona: №{room.room_number} ({room.room_type})\n"
            f"📅 Sanalar: {start_date} - {end_date}\n"
            f"👤 Mehmon: {booking.guest_name or 'Ko\'rsatilmagan'}\n"
            f"💬 Izoh: {booking.notes or 'Yo\'q'}\n"
            f"👨‍💻 Kim tomonidan: {user.full_name}"
        )

        # Send to all admins
        admins = db.query(User).filter(User.is_admin == True).all()
        for admin in admins:
            if admin.telegram_id and admin.id != user.id:  # Don't send to the creator
                await self.send_message(admin.telegram_id, text)

    async def send_booking_updated(self, db: Session, booking: Booking, room: Room, user: User, changes: dict):
        """Send notification about booking update"""
        # Format dates
        start_date = booking.start_date.strftime("%d.%m.%Y")
        end_date = booking.end_date.strftime("%d.%m.%Y")

        text = (
            f"📝 <b>Bron yangilandi</b>\n\n"
            f"🏠 Xona: №{room.room_number} ({room.room_type})\n"
            f"📅 Sanalar: {start_date} - {end_date}\n"
            f"👤 Mehmon: {booking.guest_name or 'Ko\'rsatilmagan'}\n"
            f"👨‍💻 Kim tomonidan: {user.full_name}"
        )

        # Send to all admins
        admins = db.query(User).filter(User.is_admin == True).all()
        for admin in admins:
            if admin.telegram_id and admin.id != user.id:
                await self.send_message(admin.telegram_id, text)

    async def send_booking_cancelled(self, db: Session, booking: Booking, room: Room, user: User):
        """Send notification about booking cancellation"""
        # Format dates
        start_date = booking.start_date.strftime("%d.%m.%Y")
        end_date = booking.end_date.strftime("%d.%m.%Y")

        text = (
            f"❌ <b>Bron bekor qilindi</b>\n\n"
            f"🏠 Xona: №{room.room_number} ({room.room_type})\n"
            f"📅 Sanalar: {start_date} - {end_date}\n"
            f"👤 Mehmon: {booking.guest_name or 'Ko\'rsatilmagan'}\n"
            f"👨‍💻 Kim tomonidan: {user.full_name}"
        )

        # Send to all admins
        admins = db.query(User).filter(User.is_admin == True).all()
        for admin in admins:
            if admin.telegram_id and admin.id != user.id:
                await self.send_message(admin.telegram_id, text)

    async def send_daily_report(self, db: Session):
        """Send daily report to all admins"""
        from ..models.booking import Booking
        from sqlalchemy import and_

        today = date.today()

        # Get today's check-ins
        checkins = db.query(Booking).filter(Booking.start_date == today).all()

        # Get today's check-outs
        checkouts = db.query(Booking).filter(Booking.end_date == today).all()

        # Get current occupancy
        occupied = db.query(Booking).filter(
            and_(
                Booking.start_date <= today,
                Booking.end_date >= today
            )
        ).count()

        total_rooms = db.query(Room).count()

        text = (
            f"📊 <b>Kunlik hisobot - {today.strftime('%d.%m.%Y')}</b>\n\n"
            f"📥 Bugun kirish: {len(checkins)} ta\n"
            f"📤 Bugun chiqish: {len(checkouts)} ta\n"
            f"🏠 Band xonalar: {occupied}/{total_rooms}\n"
            f"📈 Bandlik: {(occupied / total_rooms * 100):.1f}%\n\n"
            f"🔗 <a href='{self.web_app_url}'>Tizimga o'tish</a>"
        )

        # Send to all admins
        admins = db.query(User).filter(User.is_admin == True).all()
        for admin in admins:
            if admin.telegram_id:
                await self.send_message(admin.telegram_id, text)


notification_service = NotificationService()