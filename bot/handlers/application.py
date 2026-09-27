from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.states import ApplicationForm
from bot.keyboards.inline import (
    main_menu_kb, course_choice_kb, confirm_kb, cancel_kb
)
from bot.db.database import create_lead, upsert_user
from bot.services.notifier import notify_admins

router = Router()


@router.message(F.text == "📝 Записатися на перше заняття")
async def start_application(message: Message, state: FSMContext):
    await state.clear()
    await upsert_user(message.from_user.id, message.from_user.username)

    await state.set_state(ApplicationForm.parent_name)
    await message.answer(
        "Чудово! Давайте заповнимо коротку заявку.\n\n"
        "Як вас звати? (ім’я батька або мами)",
        reply_markup=cancel_kb()
    )


@router.message(ApplicationForm.parent_name)
async def process_parent_name(message: Message, state: FSMContext):
    name = message.text.strip()
    if len(name) < 2:
        await message.answer("Будь ласка, введіть ім’я (мінімум 2 символи).")
        return
    await state.update_data(parent_name=name)
    await state.set_state(ApplicationForm.child_name)
    await message.answer("Як звати дитину?")


@router.message(ApplicationForm.child_name)
async def process_child_name(message: Message, state: FSMContext):
    name = message.text.strip()
    if len(name) < 2:
        await message.answer("Будь ласка, введіть ім’я дитини.")
        return
    await state.update_data(child_name=name)
    await state.set_state(ApplicationForm.child_age)
    await message.answer("Скільки років дитині? (число від 5 до 18)")


@router.message(ApplicationForm.child_age)
async def process_child_age(message: Message, state: FSMContext):
    try:
        age = int(message.text.strip())
        if not 5 <= age <= 18:
            raise ValueError
    except ValueError:
        await message.answer("Будь ласка, введіть число від 5 до 18.")
        return

    await state.update_data(child_age=age)
    await state.set_state(ApplicationForm.course)
    await message.answer(
        "Який напрямок цікавить?",
        reply_markup=course_choice_kb()
    )


@router.callback_query(ApplicationForm.course, F.data.startswith("select_course:"))
async def process_course(callback: CallbackQuery, state: FSMContext):
    course = callback.data.split(":", 1)[1]
    await state.update_data(course=course)
    await state.set_state(ApplicationForm.phone)
    await callback.message.edit_text(
        f"Напрямок: <b>{course}</b>\n\n"
        "Вкажіть номер телефону для зв’язку (обов’язково):",
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(ApplicationForm.phone)
async def process_phone(message: Message, state: FSMContext):
    phone = message.text.strip()
    # Проста перевірка
    digits = "".join(c for c in phone if c.isdigit())
    if len(digits) < 10:
        await message.answer(
            "Будь ласка, введіть коректний номер телефону "
            "(наприклад +380XXXXXXXXX або 0XXXXXXXXX)."
        )
        return

    await state.update_data(phone=phone)
    await state.set_state(ApplicationForm.preferred_time)
    await message.answer(
        "Коли вам зручно? (можна написати текстом, наприклад «після 17:00» "
        "або «вихідні»).\n\n"
        "Або натисніть /skip, якщо поки не важливо."
    )


@router.message(ApplicationForm.preferred_time, F.text == "/skip")
async def skip_time(message: Message, state: FSMContext):
    await state.update_data(preferred_time=None)
    await show_confirmation(message, state)


@router.message(ApplicationForm.preferred_time)
async def process_time(message: Message, state: FSMContext):
    await state.update_data(preferred_time=message.text.strip())
    await show_confirmation(message, state)


async def show_confirmation(message: Message, state: FSMContext):
    data = await state.get_data()
    text = (
        "📋 <b>Перевірте заявку:</b>\n\n"
        f"👤 Батько/мама: {data['parent_name']}\n"
        f"🧒 Дитина: {data['child_name']} ({data['child_age']} років)\n"
        f"📚 Напрямок: {data['course']}\n"
        f"📱 Телефон: {data['phone']}\n"
        f"⏰ Зручний час: {data.get('preferred_time') or 'не вказано'}\n\n"
        "Усе правильно?"
    )
    await state.set_state(ApplicationForm.confirm)
    await message.answer(text, parse_mode="HTML", reply_markup=confirm_kb())


@router.callback_query(ApplicationForm.confirm, F.data == "confirm_send")
async def confirm_send(callback: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    user = callback.from_user

    try:
        lead_id = await create_lead(
            tg_user_id=user.id,
            tg_username=user.username,
            parent_name=data["parent_name"],
            child_name=data["child_name"],
            child_age=data["child_age"],
            course=data["course"],
            phone=data["phone"],
            preferred_time=data.get("preferred_time"),
        )
    except Exception as e:
        print(f"[ERROR] DB save failed: {e}")
        await callback.message.edit_text(
            "Виникла технічна помилка при збереженні. "
            "Будь ласка, напишіть нам на +380664931065."
        )
        await state.clear()
        await callback.answer()
        return

    # Надсилаємо адмінам (навіть якщо впаде — заявка вже збережена)
    try:
        await notify_admins(bot, lead_id, data, user)
    except Exception as e:
        print(f"[ERROR] Notify admins failed: {e}")

    await callback.message.edit_text(
        "✅ <b>Дякуємо! Заявку прийнято.</b>\n\n"
        "Ми зв’яжемось з вами протягом робочого дня.",
        parse_mode="HTML"
    )
    await state.clear()
    await callback.message.answer("Головне меню:", reply_markup=main_menu_kb())
    await callback.answer()


@router.callback_query(ApplicationForm.confirm, F.data == "confirm_edit")
async def confirm_edit(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ApplicationForm.parent_name)
    await callback.message.edit_text(
        "Добре, почнемо спочатку.\n\nЯк вас звати? (ім’я батька або мами)"
    )
    await callback.answer()


@router.callback_query(F.data == "cancel_form")
async def cancel_form(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("Заявку скасовано.")
    await callback.message.answer("Головне меню:", reply_markup=main_menu_kb())
    await callback.answer()
    