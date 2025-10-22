from aiogram import Router, types
from aiogram.filters import Command

from app.core.settings import settings


router = Router()

def is_admin(user_id: int) -> bool:
    return user_id in set(settings.admin_ids or [])

@router.message(Command("admin"))
async def admin_entry(m: types.Message):
    if not is_admin(m.from_user.id):
        await m.answer("Недостаточно прав.")
        return
    kb = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text="➕ Комиссии — добавить", callback_data="admin:commissions:add")],
            [types.InlineKeyboardButton(text="📋 Комиссии — список", callback_data="admin:commissions:list")],
            [types.InlineKeyboardButton(text="🗂 Обращения — просмотреть", callback_data="admin:appeals:list:0")],
        ]
    )
    await m.answer("Админ меню:", reply_markup=kb)
