from aiogram import Router, types, F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy import select
from app.core.settings import settings
from app.db.session import async_session
from app.db import models as m
from app.services.appeals import change_appeal_status, ALLOWED_TRANSITIONS

router = Router()

def is_admin(uid: int) -> bool:
    return uid in set(settings.admin_ids or [])

def status_kb(appeal_status: str, appeal_id: int) -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for st in ["IN_REVIEW", "ON_HOLD", "RESOLVED", "REJECTED", "DELETED"]:
        if st in ALLOWED_TRANSITIONS.get(appeal_status, set()):
            builder.button(text=st, callback_data=f"admin:appeal:set:{appeal_id}:{st}")
    builder.adjust(2)
    # Навигация назад к списку
    builder.row(types.InlineKeyboardButton(text="⬅️ К списку", callback_data="admin:appeals:list:0"))
    return builder.as_markup()

def appeal_full_text(a: m.Appeal, u: m.User | None, c: m.Commission | None) -> str:
    return (
        f"📝 Обращение #{a.id}\n"
        f"Статус: {a.status}\n"
        f"Комиссия: {c.title if c else a.commission_id}\n"
        f"Пользователь: @{(u.username or '-') if u else '-'} ({(u.full_name or '-') if u else '-'})\n"
        f"Контакт: {a.contact or '—'}\n"
        f"Создано: {a.created_at:%d.%m.%Y %H:%M}\n"
        f"Обновлено: {a.updated_at:%d.%m.%Y %H:%M}\n"
        f"\nТекст:\n{a.text}"
    )

@router.callback_query(F.data.startswith("admin:appeal:open:"))
async def admin_appeal_open(c: types.CallbackQuery):
    if not is_admin(c.from_user.id):
        await c.answer("Нет прав", show_alert=True); return
    appeal_id = int(c.data.split(":")[-1])

    async with async_session() as session:
        a = await session.get(m.Appeal, appeal_id)
        if not a:
            await c.message.edit_text("Обращение не найдено.")
            return
        u = await session.get(m.User, a.user_id)
        comm = await session.get(m.Commission, a.commission_id)

    await c.message.edit_text(
        appeal_full_text(a, u, comm),
        reply_markup=status_kb(a.status, a.id)
    )

@router.callback_query(F.data.startswith("admin:appeal:set:"))
async def admin_appeal_set_status(c: types.CallbackQuery):
    if not is_admin(c.from_user.id):
        await c.answer("Нет прав", show_alert=True); return
    _, _, _, appeal_id_str, new_status = c.data.split(":")
    appeal_id = int(appeal_id_str)

    async with async_session() as session:
        from aiogram import Bot
        bot: Bot = c.bot
        ok, msg = await change_appeal_status(session, bot, appeal_id, new_status)
        if ok:
            await session.commit()
        else:
            await session.rollback()

        a = await session.get(m.Appeal, appeal_id)
        u = await session.get(m.User, a.user_id) if a else None
        comm = await session.get(m.Commission, a.commission_id) if a else None

    if not a:
        await c.message.edit_text(f"{msg}\n(обращение исчезло)")
        return

    await c.message.edit_text(
        f"{msg}\n\n" + appeal_full_text(a, u, comm),
        reply_markup=status_kb(a.status, a.id)
    )
