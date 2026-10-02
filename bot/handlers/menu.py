from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.keyboards.inline import main_menu_kb, courses_kb, course_detail_kb, share_kb
from bot.db.database import get_course_prices

router = Router()


COURSES_TEXT = {
    "wedo": (
        "🤖 <b>Робототехніка</b> (орієнтовно 6–10 років)\n\n"
        "Діти збирають роботів із моторами та датчиками, програмують їх "
        "і вчаться створювати власні робототехнічні проєкти. Усе обладнання "
        "є в класі — нічого приносити не потрібно."
    ),
    "radio": (
        "🔌 <b>Радіоелектроніка</b>\n\n"
        "Пайка, прості схеми, робота з мультиметром. "
        "Спочатку збираємо на макетній платі, потім паяємо. "
        "Усе під наглядом викладача, у дружній атмосфері.  "
    ),
    "scratch": (
        "🎮 <b>Scratch</b> (орієнтовно 7–12 років)\n\n"
        "Візуальне програмування: ігри, мультики, анімації. "
        "Найкращий місток до «справжнього» коду. "
        "На заняттях працюємо на наших комп’ютерах."
    ),
    "python": (
        "🐍 <b>Python</b> (орієнтовно 12–16 років)\n\n"
        "Текстове програмування: ігри, скрипти, основи сайтів. "
        "Мінімум сухої теорії — одразу практика на проєктах."
    ),
}


@router.message(F.text == "📚 Курси")
async def show_courses(message: Message):
    await message.answer(
        "Оберіть напрямок, щоб дізнатися більше:",
        reply_markup=courses_kb()
    )


@router.callback_query(F.data.startswith("course_info:"))
async def course_info(callback: CallbackQuery):
    key = callback.data.split(":")[1]
    text = COURSES_TEXT.get(key, "Інформація тимчасово недоступна.")
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=course_detail_kb())
    await callback.answer()


@router.callback_query(F.data == "back_to_courses")
async def back_to_courses(callback: CallbackQuery):
    await callback.message.edit_text(
        "Оберіть напрямок, щоб дізнатися більше:",
        reply_markup=courses_kb(),
    )
    await callback.answer()


@router.message(F.text == "💰 Ціни")
async def show_prices(message: Message):
    prices = await get_course_prices()
    course_names = {
        "wedo": "Робототехніка",
        "radio": "Радіоелектроніка",
        "scratch": "Scratch",
        "python": "Python",
    }
    lines = ["💰 <b>Ціни</b>", ""]
    for course, name in course_names.items():
        course_price = prices.get(course)
        if course_price is None:
            continue
        lines.extend([
            f"<b>{name}</b>",
            f"• Разове заняття — {course_price['single_price']} грн (60 хв)",
            f"• Абонемент на місяць — {course_price['monthly_price']} грн (≈ 4 заняття)",
            "",
        ])
    lines.append("Усе обладнання надаємо ми. Перше заняття ні до чого не зобов’язує.")
    text = (
        "\n".join(lines)
    )
    await message.answer(text, parse_mode="HTML")


@router.message(F.text == "📞 Контакти")
async def show_contacts(message: Message):
    text = (
        "📞 <b>Контакти STEM RoboKS</b>\n\n"
        "📍 Місто: Дніпро\n"
        "📱 Телефон: +380664931065\n"
        "📸 Instagram: https://www.instagram.com/roboks_dnipro/\n\n"
        "Ми завжди на зв’язку і відповімо протягом робочого дня."
    )
    await message.answer(text, parse_mode="HTML", disable_web_page_preview=True)


@router.message(F.text == "❓ Часті питання")
async def show_faq(message: Message):
    text = (
        "❓ <b>Часті питання</b>\n\n"
        "<b>Чи потрібен власний конструктор / комп’ютер?</b>\n"
        "Ні. Усе обладнання є в класі.\n\n"
        "<b>Скільки дітей у групі?</b>\n"
        "Зазвичай 4–8 осіб.\n\n"
        "<b>Чи можна прийти на пробне?</b>\n"
        "Так, саме для цього і є «перше заняття» за 350 грн.\n\n"
        "<b>Як відбувається запис?</b>\n"
        "Залишаєте заявку → ми телефонуємо → підбираємо групу і час."
    )
    await message.answer(text, parse_mode="HTML")


@router.message(F.text == "✉️ Написати адміну")
async def contact_admin(message: Message):
    text = (
        "Ви можете написати нам безпосередньо:\n\n"
        "📱 +380664931065\n"
        "або просто залиште заявку через кнопку «Записатися» — "
        "ми самі зв’яжемося з вами."
    )
    await message.answer(text)


@router.message(F.text == "🔗 Поділитися ботом")
async def share_bot(message: Message):
    await message.answer(
        "Натисніть кнопку нижче, щоб поділитися ботом з друзями:",
        reply_markup=share_kb()
    )


@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.delete()
    await callback.message.answer(
        "Головне меню:",
        reply_markup=main_menu_kb()
    )
    await callback.answer()