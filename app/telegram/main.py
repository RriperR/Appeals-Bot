import asyncio
from aiogram import Bot, Dispatcher

from app.core.settings import settings
from app.core.logging import setup_logging
from .routers import public, apply, track


async def main():
    setup_logging()
    bot = Bot(token=settings.bot_token, parse_mode="HTML")
    dp = Dispatcher()
    dp.include_router(public.router)
    dp.include_router(apply.router)
    dp.include_router(track.router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
