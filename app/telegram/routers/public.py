from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from app.telegram.keyboards import main_menu


router = Router()

@router.message(Command("start"))
async def start(msg: Message):
    await msg.answer(
        "Добрый день! 👋\n"
        "Добро пожаловать в чат-бот комиссий.\n\n"
        "Выберите действие:",
        reply_markup=main_menu()
    )

@router.message(Command("help"))
async def help_cmd(msg: Message):
    await msg.answer(
        "Доступные команды:\n"
        "• /start — главное меню\n"
        "• /help — помощь\n"
        "• /admin — админ-меню"
    )

@router.message(Command("chatid"))
async def get_chat_id(msg: Message):
    await msg.answer(str(msg.from_user.id))
