import os
from aiogram import Bot
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session

from ..models.booking import Booking
from ..models.room import Room
from ..models.user import User
from ..config import settings


class NotificationService:
    def __init__(self):
        self.bot_token = settings.TELEGRAM_BOT_TOKEN
        self.bot = Bot(token=self.bot_token) if self.bot_token else None
        self.allowed_ids = os.getenv("ALLOWED_TELEGRAM_IDS", "").split(",")

    async def send_message(self, chat_id: int, text: str):
        """Send message to Telegram user"""
        if not self.bot:
            print(f"[Notification] Bot not configured, skipping message to {chat_id}")
            return

        try:
            await self.bot.send_message(chat_id=chat_id, text=text, parse_mode="HTML")
            print(f"[Notification] Message sent to {chat_id}")
        except Exception as e:
            print(f"[Notification] Error sending message to {chat_id}: {e}")

    async def send_booking_created(self, db: Session, booking: Booking, room: Room, user: User):
        """Send notification about new booking"""
        if not self.bot:
            return

        start_date = booking.start_date.strftime("%d.%m.%Y")
        end_date = booking.end_date.strftime("%d.%m.%Y")

        message = (
            f"✅ <b>Yangi bron yaratildi</b>\n\n"
            f"🏠 Xona: №{room.room_number} ({room.room_type})\n"
            f"📅 Sanalar: {start_date} - {end_date}\n"
            f"👤 Mehmon: {booking.guest_name or 'Ko\'rsatilmagan'}\n"
            f"👨‍💼 Yaratdi: {user.full_name}\n"
            f"🕐 Vaqt: {datetime.now().strftime('%H:%M')}"
        )

        # Send to all admins
        for telegram_id in self.allowed_ids:
            if telegram_id.strip():
                try:
                    await self.send_message(int(telegram_id.strip()), message)
                except:
                    pass

    async def send_booking_cancelled(self, db: Session, booking: Booking, room: Room, user: User):
        """Send notification about cancelled booking"""
        if not self.bot:
            return

        start_date = booking.start_date.strftime("%d.%m.%Y")
        end_date = booking.end_date.strftime("%d.%m.%Y")

        message = (
            f"❌ <b>Bron bekor qilindi</b>\n\n"
            f"🏠 Xona: №{room.room_number} ({room.room_type})\n"
            f"📅 Sanalar: {start_date} - {end_date}\n"
            f"👤 Mehmon: {booking.guest_name or 'Ko\'rsatilmagan'}\n"
            f"👨‍💼 Bekor qildi: {user.full_name}\n"
            f"🕐 Vaqt: {datetime.now().strftime('%H:%M')}"
        )

        # Send to all admins
        for telegram_id in self.allowed_ids:
            if telegram_id.strip():
                try:
                    await self.send_message(int(telegram_id.strip()), message)
                except:
                    pass

    async def send_daily_report(self, db: Session):
        """Send daily report to admins"""
        if not self.bot:
            return

        # TODO: Implement daily report logic
        pass

    async def close(self):
        """Close bot session"""
        if self.bot:
            await self.bot.session.close()


# Create global instance
notification_service = NotificationService()