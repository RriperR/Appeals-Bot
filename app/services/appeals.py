from aiogram import Bot
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db import models as m
from app.services.notifications import send_notification

ALLOWED_TRANSITIONS: dict[str, set[str]] = {
    "NEW": {"IN_REVIEW", "REJECTED", "DELETED"},
    "IN_REVIEW": {"ON_HOLD", "RESOLVED", "REJECTED"},
    "ON_HOLD": {"IN_REVIEW", "RESOLVED", "REJECTED"},
    "RESOLVED": set(),   # финал
    "REJECTED": set(),   # финал
    "DELETED": set(),    # финал
}

async def change_appeal_status(
    session: AsyncSession,
    bot: Bot,
    appeal_id: int,
    new_status: str,
) -> tuple[bool, str]:
    appeal = await session.get(m.Appeal, appeal_id)
    if not appeal:
        return False, "Обращение не найдено."

    cur = appeal.status
    if cur == new_status:
        return False, f"Статус уже {new_status}."

    allowed = ALLOWED_TRANSITIONS.get(cur, set())
    if new_status not in allowed:
        return False, f"Переход {cur} → {new_status} не разрешён."

    appeal.status = new_status
    await session.flush()

    # найдём telegram_id владельца обращения
    user = (await session.execute(
        select(m.User).where(m.User.id == appeal.user_id)
    )).scalar_one_or_none()

    if user and user.telegram_id:
        await send_notification(
            session=session,
            bot=bot,
            telegram_id=user.telegram_id,
            appeal_id=appeal.id,
            text=f"📢 Статус вашего обращения #{appeal.id}: {new_status}",
        )
    return True, "Статус обновлён."
