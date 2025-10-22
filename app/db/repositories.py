from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import models as m

class CommissionRepo:
    @staticmethod
    async def by_title(session: AsyncSession, title: str) -> m.Commission | None:
        return (await session.execute(
            select(m.Commission).where(m.Commission.title.ilike(title))
        )).scalar_one_or_none()

    @staticmethod
    async def create(session: AsyncSession, title: str, description: str | None) -> m.Commission:
        obj = m.Commission(title=title.strip(), description=(description or "").strip())
        session.add(obj)
        await session.flush()
        return obj

    @staticmethod
    async def list_active(session: AsyncSession) -> list[m.Commission]:
        rows = (await session.execute(
            select(m.Commission).where(m.Commission.is_active == True).order_by(m.Commission.title)  # noqa
        )).scalars().all()
        return list(rows)

class UserRepo:
    @staticmethod
    async def upsert_from_telegram(session: AsyncSession, tg_id: int, full_name: str | None, username: str | None) -> m.User:
        user = (await session.execute(
            select(m.User).where(m.User.telegram_id == tg_id)
        )).scalar_one_or_none()
        if not user:
            user = m.User(telegram_id=tg_id, full_name=full_name, username=username, is_active=True)
            session.add(user)
            await session.flush()
        else:
            # лёгкое обновление ФИО/ника
            changed = False
            if full_name and user.full_name != full_name:
                user.full_name = full_name; changed = True
            if username and user.username != username:
                user.username = username; changed = True
            if changed:
                await session.flush()
        return user

class AppealRepo:
    @staticmethod
    async def create(
        session: AsyncSession,
        user_id: int,
        commission_id: int,
        text: str,
        contact: str | None,
        files: list[tuple[str, str | None, str | None]]  # (file_id, file_name, mime)
    ) -> m.Appeal:
        appeal = m.Appeal(user_id=user_id, commission_id=commission_id, text=text.strip(), contact=contact)
        session.add(appeal)
        await session.flush()
        for fid, fname, mime in files:
            session.add(m.AppealFile(appeal_id=appeal.id, telegram_file_id=fid, file_name=fname, mime_type=mime))
        await session.flush()
        return appeal

    @staticmethod
    async def count_all(session: AsyncSession) -> int:
        return (await session.execute(select(func.count()).select_from(m.Appeal))).scalar_one()

    @staticmethod
    async def list_admin_page(session: AsyncSession, page: int, page_size: int = 10):
        q = (
            select(m.Appeal, m.User, m.Commission)
            .join(m.User, m.User.id == m.Appeal.user_id)
            .join(m.Commission, m.Commission.id == m.Appeal.commission_id)
            .order_by(m.Appeal.created_at.desc())
            .limit(page_size).offset(page * page_size)
        )
        return (await session.execute(q)).all()
