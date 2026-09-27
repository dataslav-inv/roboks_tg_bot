from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from config import settings
from bot.db.database import (
    get_recent_leads,
    get_lead,
    update_lead_status,
    get_stats,
    get_course_prices,
    update_course_price,
)
from bot.keyboards.inline import admin_lead_kb

router = Router()


def is_admin(user_id: int) -> bool:
    return user_id in settings.admin_ids


COURSE_NAMES = {
    "wedo": "Робототехніка",
    "radio": "Радіоелектроніка",
    "scratch": "Scratch",
    "python": "Python",
}


@router.message(Command("prices"))
async def cmd_prices(message: Message):
    if not is_admin(message.from_user.id):
        return

    prices = await get_course_prices()
    lines = ["💰 <b>Поточні ціни:</b>", ""]
    for course, name in COURSE_NAMES.items():
        course_price = prices.get(course)
        if course_price is None:
            continue
        lines.append(
            f"<b>{name}</b> ({course}): "
            f"{course_price['single_price']} / {course_price['monthly_price']} грн"
        )
    lines.extend([
        "",
        "Зміна: /set_price &lt;курс&gt; &lt;разове&gt; &lt;місячний&gt;",
        "Наприклад: /set_price python 400 1400",
    ])
    await message.answer("\n".join(lines), parse_mode="HTML")


@router.message(Command("set_price"))
async def cmd_set_price(message: Message):
    if not is_admin(message.from_user.id):
        return

    parts = message.text.split()
    if len(parts) != 4 or parts[1].lower() not in COURSE_NAMES:
        await message.answer(
            "Використання: /set_price &lt;курс&gt; &lt;разове&gt; &lt;місячний&gt;\n"
            "Курси: wedo, radio, scratch, python",
            parse_mode="HTML",
        )
        return

    try:
        single_price = int(parts[2])
        monthly_price = int(parts[3])
        if single_price < 0 or monthly_price < 0:
            raise ValueError
    except ValueError:
        await message.answer("Ціни мають бути невід’ємними цілими числами.")
        return

    course = parts[1].lower()
    await update_course_price(course, single_price, monthly_price)
    await message.answer(
        f"✅ Ціни для <b>{COURSE_NAMES[course]}</b> оновлено:\n"
        f"разове — {single_price} грн, місячний абонемент — {monthly_price} грн.",
        parse_mode="HTML",
    )


@router.message(Command("leads"))
async def cmd_leads(message: Message):
    if not is_admin(message.from_user.id):
        return

    leads = await get_recent_leads(10)
    if not leads:
        await message.answer("Заявок поки немає.")
        return

    lines = ["📋 <b>Останні 10 заявок:</b>\n"]
    for lead in leads:
        status_emoji = {
            "new": "🆕",
            "in_progress": "🔄",
            "done": "✅",
            "cancelled": "❌",
        }.get(lead.status, "•")
        lines.append(
            f"{status_emoji} <b>#{lead.id}</b> — {lead.child_name} "
            f"({lead.child_age}), {lead.course}, {lead.phone}\n"
            f"   статус: {lead.status} | {lead.created_at[:16]}"
        )
    await message.answer("\n".join(lines), parse_mode="HTML")


@router.message(Command("lead_id"))
async def cmd_lead_id(message: Message):
    if not is_admin(message.from_user.id):
        return

    parts = message.text.split()
    if len(parts) < 2 or not parts[1].isdigit():
        await message.answer("Використання: /lead_id 123")
        return

    lead = await get_lead(int(parts[1]))
    if not lead:
        await message.answer("Заявку не знайдено.")
        return

    username = f"@{lead.tg_username}" if lead.tg_username else "немає"
    text = (
        f"📄 <b>Заявка #{lead.id}</b>\n\n"
        f"Статус: <b>{lead.status}</b>\n"
        f"Батько/мама: {lead.parent_name}\n"
        f"Дитина: {lead.child_name} ({lead.child_age})\n"
        f"Напрямок: {lead.course}\n"
        f"Телефон: {lead.phone}\n"
        f"Час: {lead.preferred_time or '—'}\n"
        f"Telegram: {username} (id: {lead.tg_user_id})\n"
        f"Створено: {lead.created_at}\n"
        f"Оновлено: {lead.updated_at}"
    )
    await message.answer(text, parse_mode="HTML", reply_markup=admin_lead_kb(lead.id))


@router.message(Command("stats"))
async def cmd_stats(message: Message):
    if not is_admin(message.from_user.id):
        return

    stats = await get_stats()
    text = (
        "📊 <b>Статистика заявок</b>\n\n"
        f"Сьогодні: <b>{stats['today']}</b>\n"
        f"За 7 днів: <b>{stats['week']}</b>\n"
        f"Нових (status=new): <b>{stats['new']}</b>"
    )
    await message.answer(text, parse_mode="HTML")


@router.callback_query(F.data.startswith("admin_status:"))
async def admin_change_status(callback: CallbackQuery, bot: Bot):
    if not is_admin(callback.from_user.id):
        await callback.answer("Немає доступу", show_alert=True)
        return

    _, lead_id_str, new_status = callback.data.split(":")
    lead_id = int(lead_id_str)

    ok = await update_lead_status(lead_id, new_status)
    if not ok:
        await callback.answer("Заявку не знайдено", show_alert=True)
        return

    status_names = {
        "in_progress": "В роботі",
        "done": "Закрито",
        "cancelled": "Скасовано",
    }
    await callback.answer(f"Статус змінено на «{status_names.get(new_status, new_status)}»")
    await callback.message.edit_reply_markup(reply_markup=admin_lead_kb(lead_id))
    