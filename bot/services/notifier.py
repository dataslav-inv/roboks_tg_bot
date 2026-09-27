from aiogram import Bot
from aiogram.types import User
from typing import Optional

from config import settings
from bot.keyboards.inline import admin_lead_kb


async def notify_admins(bot: Bot, lead_id: int, data: dict, user: User):
    username = f"@{user.username}" if user.username else "немає"
    profile_link = f'<a href="tg://user?id={user.id}">Профіль користувача</a>'

    text = (
        f"🆕 <b>Нова заявка #{lead_id}</b>\n\n"
        f"👤 Батько/мама: <b>{data['parent_name']}</b>\n"
        f"🧒 Дитина: <b>{data['child_name']}</b> ({data['child_age']} років)\n"
        f"📚 Напрямок: <b>{data['course']}</b>\n"
        f"📱 Телефон: <b>{data['phone']}</b>\n"
        f"⏰ Зручний час: {data.get('preferred_time') or 'не вказано'}\n\n"
        f"Telegram: {username}\n"
        f"{profile_link}\n"
        f"ID: <code>{user.id}</code>"
    )

    for admin_id in settings.admin_ids:
        try:
            await bot.send_message(
                admin_id,
                text,
                parse_mode="HTML",
                reply_markup=admin_lead_kb(lead_id),
                disable_web_page_preview=True,
            )
        except Exception as e:
            print(f"[ERROR] Не вдалося надіслати адміну {admin_id}: {e}")
