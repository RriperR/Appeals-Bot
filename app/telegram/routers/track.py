from aiogram import Router, types, F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy import select, func
from sqlalchemy.orm import aliased

from app.db.session import async_session
from app.db import models as m
from app.utils.formatting import format_appeal_card


router = Router()
PAGE_SIZE = 5


def nav_kb(page: int, total: int) -> types.InlineKeyboardMarkup | None:
    rows = []
    builder = InlineKeyboardBuilder()
    if page > 0:
        builder.button(text="⬅️ Предыдущие", callback_data=f"user:appeals:page:{page-1}")
    if (page + 1) * PAGE_SIZE < total:
        builder.button(text="Следующие ➡️", callback_data=f"user:appeals:page:{page+1}")
    if not builder.buttons:
        return None
    builder.adjust(2)
    return builder.as_markup()


async def render_user_page(msg: types.Message, telegram_id: int, page: int):
    async with async_session() as session:
        user = (await session.execute(
            select(m.User).where(m.User.telegram_id == telegram_id)
        )).scalar_one_or_none()
        if not user:
            await msg.answer("У вас пока нет обращений.")
            return

        total = (await session.execute(
            select(func.count()).select_from(m.Appeal).where(m.Appeal.user_id == user.id)
        )).scalar_one()

        if total == 0:
            await msg.answer("У вас пока нет обращений.")
            return

        AF = aliased(m.AppealFile)
        rows = (await session.execute(
            select(
                m.Appeal.id,
                m.Appeal.status,
                m.Appeal.created_at,
                m.Appeal.contact,
                m.Appeal.text,
                m.Commission.title,
                func.count(AF.id).label("files_count"),
            )
            .join(m.Commission, m.Commission.id == m.Appeal.commission_id)
            .outerjoin(AF, AF.appeal_id == m.Appeal.id)
            .where(m.Appeal.user_id == user.id)
            .group_by(m.Appeal.id, m.Commission.title)
            .order_by(m.Appeal.created_at.desc())
            .limit(PAGE_SIZE)
            .offset(page * PAGE_SIZE)
        )).all()

    text_parts = [f"📋 Ваши обращения (стр. {page+1}) • всего: {total}"]
    for aid, status, created_at, contact, text, title, files_count in rows:
        text_parts.append(
            "\n" + format_appeal_card(
                appeal_id=aid,
                commission_title=title,
                status=status,
                created_at=created_at,
                contact=contact,
                text=text,
                files_count=files_count,
            )
        )

    text = "\n\n".join(text_parts)
    kb = nav_kb(page, total)
    await msg.answer(text, reply_markup=kb)


@router.message(F.text == "Отследить статус")
async def track(msg: types.Message):
    await render_user_page(msg, telegram_id=msg.from_user.id, page=0)


@router.callback_query(F.data.startswith("user:appeals:page:"))
async def user_page(c: types.CallbackQuery):
    page = int(c.data.split(":")[-1])
    await c.message.edit_text("Обновляю список…")
    # перерисуем свежим сообщением (edit_text длинного списка может упираться в лимиты)
    await render_user_page(c.message, telegram_id=c.from_user.id, page=page)
