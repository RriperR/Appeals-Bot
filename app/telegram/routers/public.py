from aiogram import Router, types
from aiogram.filters import Command
from app.telegram.keyboards import main_menu


router = Router()

@router.message(Command("start"))
async def start(m: types.Message):
    await m.answer(
        "Добрый день! 👋\n"
        "Добро пожаловать в чат-бот комиссий.\n\n"
        "Выберите действие:",
        reply_markup=main_menu()
    )

@router.message(Command("help"))
async def help_cmd(m: types.Message):
    await m.answer(
        "Доступные команды:\n"
        "• /start — главное меню\n"
        "• /help — помощь\n"
        "• /admin — админ-меню"
    )
