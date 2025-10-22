from datetime import datetime

from aiogram import Bot
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db import models as m


async def send_notification(
    session: AsyncSession,
    bot: Bot,
    user_id: int | None = None,
    telegram_id: int | None = None,
    text: str = "",
    appeal_id: int | None = None,
) -> None:
    """
    Если известен user_id — используем его, иначе найдём по telegram_id.
    Сохраняем нотификацию и пробуем отправить в Telegram.
    """
    if not user_id and telegram_id:
        user = (await session.execute(
            select(m.User).where(m.User.telegram_id == telegram_id)
        )).scalar_one_or_none()
        if user:
            user_id = user.id

    notif = m.Notification(user_id=user_id or 0, appeal_id=appeal_id, text=text)
    session.add(notif)
    await session.flush()

    # отправка в Telegram (если знаем telegram_id)
    if telegram_id:
        try:
            await bot.send_message(chat_id=telegram_id, text=text)
            notif.sent_ok = True
            notif.sent_at = datetime.utcnow()
        except Exception as e:  # noqa
            notif.error = str(e)

    await session.flush()
