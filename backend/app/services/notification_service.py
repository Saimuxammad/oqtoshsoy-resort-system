from typing import List, Optional
from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime
from sqlalchemy.orm import Session
from ..config import settings
from ..models.user import User
from ..models.room import Room
from ..models.booking import Booking


class NotificationService:
    def __init__(self):
        self.bot = Bot(token=settings.telegram_bot_token)

    async def send_booking_created(
            self,
            db: Session,
            booking: Booking,
            room: Room,
            created_by: User
    ):
        """Send notification when new booking is created"""
        # Get all admin users
        admins = db.query(User).filter(User.is_admin == True).all()

        message = (
            "🆕 <b>Yangi bron yaratildi</b>\n\n"
            f"🏨 Xona: №{room.room_number} ({room.room_type})\n"
            f"📅 Sanalar: {booking.start_date.strftime('%d.%m.%Y')} - {booking.end_date.strftime('%d.%m.%Y')}\n"
            f"👤 Mehmon: {booking.guest_name or 'Ko\'rsatilmagan'}\n"
            f"✍️ Yaratuvchi: {created_by.first_name} {created_by.last_name or ''}\n"
            f"🕐 Vaqt: {datetime.now().strftime('%d.%m.%Y %H:%M')}"
        )

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📱 Tizimga o'tish", web_app={"url": settings.web_app_url})]
        ])

        for admin in admins:
            try:
                await self.bot.send_message(
                    chat_id=admin.telegram_id,
                    text=message,
                    parse_mode="HTML",
                    reply_markup=keyboard
                )
            except Exception as e:
                print(f"Failed to send notification to {admin.telegram_id}: {e}")

    async def send_booking_cancelled(
            self,
            db: Session,
            booking: Booking,
            room: Room,
            cancelled_by: User
    ):
        """Send notification when booking is cancelled"""
        admins = db.query(User).filter(User.is_admin == True).all()

        message = (
            "❌ <b>Bron bekor qilindi</b>\n\n"
            f"🏨 Xona: №{room.room_number} ({room.room_type})\n"
            f"📅 Sanalar: {booking.start_date.strftime('%d.%m.%Y')} - {booking.end_date.strftime('%d.%m.%Y')}\n"
            f"👤 Mehmon: {booking.guest_name or 'Ko\'rsatilmagan'}\n"
            f"🚫 Bekor qiluvchi: {cancelled_by.first_name} {cancelled_by.last_name or ''}\n"
            f"🕐 Vaqt: {datetime.now().strftime('%d.%m.%Y %H:%M')}"
        )

        for admin in admins:
            try:
                await self.bot.send_message(
                    chat_id=admin.telegram_id,
                    text=message,
                    parse_mode="HTML"
                )
            except Exception as e:
                print(f"Failed to send notification to {admin.telegram_id}: {e}")

    async def send_daily_report(self, db: Session):
        """Send daily occupancy report to admins"""
        from datetime import date
        today = date.today()

        # Get today's bookings
        bookings = db.query(Booking).filter(
            Booking.start_date <= today,
            Booking.end_date >= today
        ).all()

        total_rooms = db.query(Room).count()
        occupied_rooms = len(bookings)
        occupancy_rate = (occupied_rooms / total_rooms * 100) if total_rooms > 0 else 0

        message = (
            "📊 <b>Kunlik hisobot</b>\n\n"
            f"📅 Sana: {today.strftime('%d.%m.%Y')}\n"
            f"🏨 Jami xonalar: {total_rooms}\n"
            f"🔴 Band xonalar: {occupied_rooms}\n"
            f"🟢 Bo'sh xonalar: {total_rooms - occupied_rooms}\n"
            f"📈 Bandlik: {occupancy_rate:.1f}%\n\n"
        )

        if bookings:
            message += "<b>Band xonalar ro'yxati:</b>\n"
            for booking in bookings[:10]:  # Show first 10
                room = booking.room
                message += f"• №{room.room_number} - {booking.guest_name or 'Mehmon'}\n"

            if len(bookings) > 10:
                message += f"\n<i>Va yana {len(bookings) - 10} ta xona...</i>"

        admins = db.query(User).filter(User.is_admin == True).all()

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📱 Batafsil ko'rish", web_app={"url": settings.web_app_url})]
        ])

        for admin in admins:
            try:
                await self.bot.send_message(
                    chat_id=admin.telegram_id,
                    text=message,
                    parse_mode="HTML",
                    reply_markup=keyboard
                )
            except Exception as e:
                print(f"Failed to send daily report to {admin.telegram_id}: {e}")


notification_service = NotificationService()

