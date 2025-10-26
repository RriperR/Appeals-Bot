from aiogram import Router, types, F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy import select
from app.db.session import async_session
from app.db import models as m

router = Router()

@router.message(F.text == "Описание комиссий")
async def commissions_overview(m: types.Message):
    async with async_session() as session:
        rows = (await session.execute(
            select(m.Commission.id, m.Commission.title)
            .where(m.Commission.is_active == True)  # noqa: E712
            .order_by(m.Commission.title)
        )).all()
    if not rows:
        await m.answer("Пока нет активных комиссий.")
        return
    kb = InlineKeyboardBuilder()
    for cid, title in rows:
        kb.button(text=title, callback_data=f"pub:commission:{cid}")
    kb.adjust(1)
    await m.answer("Выберите комиссию для описания:", reply_markup=kb.as_markup())

@router.callback_query(F.data.startswith("pub:commission:"))
async def commission_desc(c: types.CallbackQuery):
    cid = int(c.data.split(":")[-1])
    async with async_session() as session:
        comm = await session.get(m.Commission, cid)
    if not comm or not comm.is_active:
        await c.answer("Комиссия недоступна", show_alert=True); return
    text = f"📌 <b>{comm.title}</b>\n\n{comm.description or 'Описание не указано.'}"
    await c.message.edit_text(text, reply_markup=types.InlineKeyboardMarkup(
        inline_keyboard=[[types.InlineKeyboardButton(text="⬅️ Назад", callback_data="pub:commissions:back")]]
    ))

@router.callback_query(F.data == "pub:commissions:back")
async def commissions_back(c: types.CallbackQuery):
    # перерисуем список
    await commissions_overview(c.message)
