import asyncio
import logging
from pathlib import Path
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.settings import settings
from app.db.base import Base
from app.db import models  # noqa: F401  # ВАЖНО: чтобы Base.metadata наполнилась


config = context.config

# Логирование: работаем и без alembic.ini
cfg_file = config.config_file_name
if cfg_file and Path(cfg_file).exists():
    fileConfig(cfg_file)
else:
    logging.basicConfig(level=logging.INFO)

target_metadata = Base.metadata


def run_migrations_offline():
    """Offline режим — генерим SQL без подключения."""
    url = settings.database_url
    if not url:
        raise RuntimeError("DATABASE_URL не задан. Проверьте .env")
    context.configure(
        url=url,  # offline ок и с async-схемой
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    """Синхронная часть, которую Alembic ожидает внутри run_sync()."""
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online():
    """Online режим — асинхронное подключение к БД."""
    url = settings.database_url
    if not url:
        raise RuntimeError("DATABASE_URL не задан. Проверьте .env")

    engine = create_async_engine(url, poolclass=pool.NullPool, future=True)

    async with engine.connect() as conn:
        # ВАЖНО: прогоняем синхронные миграции внутри async-коннекта
        await conn.run_sync(do_run_migrations)

    await engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
