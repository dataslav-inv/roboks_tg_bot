from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from bot.keyboards.inline import main_menu_kb
from bot.db.database import upsert_user

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await upsert_user(message.from_user.id, message.from_user.username)

    text = (
        "Привіт! 👋\n\n"
        "Я бот <b>STEM-школи RoboKS</b> у Дніпрі.\n"
        "Ми вчимо дітей збирати роботів, паяти схеми та програмувати "
        "(робототехніка, радіоелектроніка, Scratch і Python).\n\n"
        "Оберіть, що вас цікавить:"
    )
    await message.answer(text, reply_markup=main_menu_kb(), parse_mode="HTML")


@router.message(Command("help"))
async def cmd_help(message: Message):
    text = (
        "📋 <b>Доступні команди:</b>\n\n"
        "/start — головне меню\n"
        "/help — ця довідка\n\n"
        "Ви також можете користуватися кнопками меню.\n"
        "Якщо хочете записатися — натисніть «Записатися на перше заняття»."
    )
    await message.answer(text, parse_mode="HTML")
    