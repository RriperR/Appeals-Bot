import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.core.settings import settings
from app.core.logging import setup_logging
from .routers import public, apply, track, admin, admin_commissions, admin_appeals


async def main():
    setup_logging()
    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()
    dp.include_router(public.router)
    dp.include_router(apply.router)
    dp.include_router(track.router)
    dp.include_router(admin.router)
    dp.include_router(admin_commissions.router)
    dp.include_router(admin_appeals.router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
