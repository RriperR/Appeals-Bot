from aiogram import Router, types, F

from app.core.settings import settings
from app.db.session import async_session
from app.db.repositories import AppealRepo


router = Router()
PAGE_SIZE = 10

def is_admin(uid: int) -> bool:
    return uid in set(settings.admin_ids or [])

def appeal_admin_line(a, u, c) -> str:
    # a = Appeal, u = User, c = Commission
    preview = a.text.strip().replace("\n", " ")
    if len(preview) > 80: preview = preview[:80] + "…"
    return (
        f"#{a.id} • {a.status} • {a.created_at:%d.%m %H:%M}\n"
        f"Комиссия: {c.title}\n"
        f"Пользователь: @{u.username or '-'} ({u.full_name or '-'})\n"
        f"Контакт: {a.contact or '—'}\n"
        f"Текст: {preview}"
    )

@router.callback_query(F.data.startswith("admin:appeals:list:"))
async def admin_appeals_list(c: types.CallbackQuery):
    if not is_admin(c.from_user.id):
        await c.answer("Нет прав", show_alert=True); return
    page = int(c.data.split(":")[-1])
    async with async_session() as session:
        total = await AppealRepo.count_all(session)
        rows = await AppealRepo.list_admin_page(session, page, PAGE_SIZE)

    if not rows:
        await c.message.edit_text("Обращений нет.")
        return

    text_parts = [f"🗂 Обращения (стр. {page+1}) • всего: {total}"]
    for a, u, comm in rows:
        text_parts.append("\n" + appeal_admin_line(a, u, comm))
    text = "\n\n".join(text_parts)

    rows_buttons = [
        [types.InlineKeyboardButton(text=f"Открыть #{a.id}", callback_data=f"admin:appeal:open:{a.id}")]
        for a, _, _ in rows
    ]
    nav = []
    if page > 0:
        nav.append(types.InlineKeyboardButton(text="⬅️ Предыдущие", callback_data=f"admin:appeals:list:{page - 1}"))
    if (page + 1) * PAGE_SIZE < total:
        nav.append(types.InlineKeyboardButton(text="Следующие ➡️", callback_data=f"admin:appeals:list:{page + 1}"))

    kb = types.InlineKeyboardMarkup(inline_keyboard=rows_buttons + ([nav] if nav else []))
    await c.message.edit_text(text, reply_markup=kb)
