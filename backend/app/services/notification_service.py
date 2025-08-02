import asyncio
from aiogram import Bot
from aiogram.types import ParseMode
from typing import List, Optional
from sqlalchemy.orm import Session
from ..models.user import User
from ..models.booking import Booking
from ..models.room import Room
from ..config import settings


class NotificationService:
    def __init__(self):
        self.bot = Bot(token=settings.TELEGRAM_BOT_TOKEN) if settings.TELEGRAM_BOT_TOKEN else None
        self.allowed_ids = settings.ALLOWED_TELEGRAM_IDS if hasattr(settings, 'ALLOWED_TELEGRAM_IDS') else []

    async def send_message(self, chat_id: int, text: str, parse_mode: ParseMode = ParseMode.HTML):
        """Send message to Telegram user"""
        if not self.bot:
            print(f"[NotificationService] Bot not configured, skipping message to {chat_id}")
            return

        try:
            await self.bot.send_message(chat_id=chat_id, text=text, parse_mode=parse_mode)
            print(f"[NotificationService] Message sent to {chat_id}")
        except Exception as e:
            print(f"[NotificationService] Error sending message to {chat_id}: {e}")

    async def send_to_admins(self, text: str):
        """Send message to all admin users"""
        if not self.bot:
            return

        for admin_id in self.allowed_ids:
            await self.send_message(admin_id, text)

    async def send_booking_created(self, db: Session, booking: Booking, room: Room, user: User):
        """Send notification about new booking"""
        text = f"""
🆕 <b>Yangi bron yaratildi!</b>

🏠 Xona: №{room.room_number} ({room.room_type})
📅 Sanalar: {booking.start_date} - {booking.end_date}
👤 Mehmon: {booking.guest_name or 'Ko\'rsatilmagan'}
🕒 Yaratilgan: {booking.created_at.strftime('%d.%m.%Y %H:%M')}
👨‍💼 Yaratuvchi: {user.full_name} (@{user.username or 'username_yo\'q'})

#{room.room_type.replace(' ', '_')} #yangi_bron
"""
        await self.send_to_admins(text)

    async def send_booking_updated(self, db: Session, booking: Booking, room: Room, user: User, changes: dict):
        """Send notification about booking update"""
        changes_text = "\n".join([f"• {k}: {v['old']} → {v['new']}" for k, v in changes.items()])

        text = f"""
✏️ <b>Bron yangilandi!</b>

🏠 Xona: №{room.room_number} ({room.room_type})
📅 Yangi sanalar: {booking.start_date} - {booking.end_date}
👤 Mehmon: {booking.guest_name or 'Ko\'rsatilmagan'}

📝 O'zgarishlar:
{changes_text}

👨‍💼 Yangiladi: {user.full_name} (@{user.username or 'username_yo\'q'})

#{room.room_type.replace(' ', '_')} #bron_yangilandi
"""
        await self.send_to_admins(text)

    async def send_booking_cancelled(self, db: Session, booking: Booking, room: Room, user: User):
        """Send notification about booking cancellation"""
        text = f"""
❌ <b>Bron bekor qilindi!</b>

🏠 Xona: №{room.room_number} ({room.room_type})
📅 Sanalar: {booking.start_date} - {booking.end_date}
👤 Mehmon: {booking.guest_name or 'Ko\'rsatilmagan'}
👨‍💼 Bekor qildi: {user.full_name} (@{user.username or 'username_yo\'q'})

#{room.room_type.replace(' ', '_')} #bron_bekor_qilindi
"""
        await self.send_to_admins(text)

    async def send_daily_report(self, db: Session):
        """Send daily report to admins"""
        from datetime import date, timedelta
        from sqlalchemy import and_

        today = date.today()
        tomorrow = today + timedelta(days=1)

        # Get today's bookings
        today_bookings = db.query(Booking).filter(
            and_(
                Booking.start_date <= today,
                Booking.end_date >= today
            )
        ).all()

        # Get tomorrow's check-ins
        tomorrow_checkins = db.query(Booking).filter(
            Booking.start_date == tomorrow
        ).all()

        # Get today's check-outs
        today_checkouts = db.query(Booking).filter(
            Booking.end_date == today
        ).all()

        # Count available rooms
        total_rooms = db.query(Room).count()
        occupied_rooms = len(today_bookings)
        available_rooms = total_rooms - occupied_rooms

        text = f"""
📊 <b>Kunlik hisobot - {today.strftime('%d.%m.%Y')}</b>

🏠 <b>Xonalar holati:</b>
• Jami xonalar: {total_rooms}
• Band xonalar: {occupied_rooms}
• Bo'sh xonalar: {available_rooms}
• Bandlik darajasi: {(occupied_rooms / total_rooms * 100):.1f}%

📥 <b>Bugun chiqish ({len(today_checkouts)} ta):</b>
"""

        for booking in today_checkouts:
            text += f"• №{booking.room.room_number} - {booking.guest_name or 'Mehmon'}\n"

        text += f"\n📤 <b>Ertaga kirish ({len(tomorrow_checkins)} ta):</b>\n"

        for booking in tomorrow_checkins:
            text += f"• №{booking.room.room_number} - {booking.guest_name or 'Mehmon'}\n"

        text += "\n#kunlik_hisobot"

        await self.send_to_admins(text)


# Create singleton instance
notification_service = NotificationService()