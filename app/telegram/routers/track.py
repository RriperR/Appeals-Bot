from aiogram import Router, types, F
from sqlalchemy import select, func
from app.db.session import async_session
from app.db import models as m
from app.utils.formatting import format_appeal_card


router = Router()

PAGE_SIZE = 5

@router.message(F.text == "Отследить статус")
async def track(m: types.Message):
    page = 0
    await send_page(m.chat.id, m.from_user.id, page, reply_to=m)

async def send_page(chat_id: int, telegram_id: int, page: int, reply_to: types.Message | None = None):
    async with async_session() as session:
        user = (await session.execute(
            select(m.User).where(m.User.telegram_id == telegram_id)
        )).scalar_one_or_none()
        if not user:
            text = "У вас пока нет обращений."
            if reply_to:
                await reply_to.answer(text)
            return

        total = (await session.execute(
            select(func.count()).select_from(m.Appeal).where(m.Appeal.user_id == user.id)
        )).scalar_one()
        if not total:
            if reply_to:
                await reply_to.answer("У вас пока нет обращений.")
            return

        rows = (await session.execute(
            select(m.Appeal, m.Commission.title)
            .join(m.Commission, m.Commission.id == m.Appeal.commission_id)
            .where(m.Appeal.user_id == user.id)
            .order_by(m.Appeal.created_at.desc())
            .limit(PAGE_SIZE)
            .offset(page * PAGE_SIZE)
        )).all()

    for appeal, title in rows:
        msg = format_appeal_card(
            appeal.id, title, appeal.status, appeal.created_at,
            appeal.contact, appeal.text, files_count=len(appeal.files or []),
        )
        await reply_to.answer(msg)
    # навигация добавим после базового happy-path
