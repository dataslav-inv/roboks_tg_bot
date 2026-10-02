from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder


def main_menu_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="📝 Записатися на перше заняття"))
    builder.row(
        KeyboardButton(text="📚 Курси"),
        KeyboardButton(text="💰 Ціни"),
    )
    builder.row(
        KeyboardButton(text="📞 Контакти"),
        KeyboardButton(text="❓ Часті питання"),
    )
    builder.row(KeyboardButton(text="✉️ Написати адміну"))
    builder.row(KeyboardButton(text="🔗 Поділитися ботом"))
    return builder.as_markup(resize_keyboard=True)


def courses_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Робототехніка (6–10 років)", callback_data="course_info:wedo"))
    builder.row(InlineKeyboardButton(text="Радіоелектроніка", callback_data="course_info:radio"))
    builder.row(InlineKeyboardButton(text="Scratch (7–12 років)", callback_data="course_info:scratch"))
    builder.row(InlineKeyboardButton(text="Python (12–16 років)", callback_data="course_info:python"))
    builder.row(InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_menu"))
    return builder.as_markup()


def course_detail_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="⬅️ Назад до курсів", callback_data="back_to_courses"))
    return builder.as_markup()


def course_choice_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Робототехніка", callback_data="select_course:Робототехніка"))
    builder.row(InlineKeyboardButton(text="Радіоелектроніка", callback_data="select_course:Радіоелектроніка"))
    builder.row(InlineKeyboardButton(text="Scratch", callback_data="select_course:Scratch"))
    builder.row(InlineKeyboardButton(text="Python", callback_data="select_course:Python"))
    builder.row(InlineKeyboardButton(text="Ще не визначились", callback_data="select_course:Ще не визначились"))
    builder.row(InlineKeyboardButton(text="❌ Скасувати", callback_data="cancel_form"))
    return builder.as_markup()


def confirm_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Надіслати", callback_data="confirm_send"),
        InlineKeyboardButton(text="✏️ Змінити", callback_data="confirm_edit"),
    )
    builder.row(InlineKeyboardButton(text="❌ Скасувати", callback_data="cancel_form"))
    return builder.as_markup()


def cancel_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="❌ Скасувати", callback_data="cancel_form"))
    return builder.as_markup()


def admin_lead_kb(lead_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🔄 В роботі", callback_data=f"admin_status:{lead_id}:in_progress"),
        InlineKeyboardButton(text="✅ Закрито", callback_data=f"admin_status:{lead_id}:done"),
    )
    builder.row(InlineKeyboardButton(text="❌ Скасовано", callback_data=f"admin_status:{lead_id}:cancelled"))
    return builder.as_markup()


def share_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="Поділитися ботом",
        switch_inline_query="Рекомендую бота STEM-школи RoboKS у Дніпрі 🤖"
    ))
    return builder.as_markup()
