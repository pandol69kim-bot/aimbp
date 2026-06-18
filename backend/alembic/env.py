import asyncio
import os
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

from app.models.user import User
from app.models.lyrics import Lyrics
from app.models.track import Track
from app.models.album import Album, AlbumTrack
from app.models.arrangement import Arrangement
from app.models.vocal import VocalLibrary, Vocal
from app.models.mastering import Mastering
from app.models.cover import Cover
from app.core.database import Base

target_metadata = Base.metadata

# DATABASE_URL 환경변수에서 async URL 가져오기
_db_url = os.getenv("DATABASE_URL", config.get_main_option("sqlalchemy.url", ""))
# asyncpg URL은 그대로 사용 (async_engine_from_config에 전달)
ASYNC_URL = _db_url if _db_url else "postgresql+asyncpg://aimbp:aimbp1234@db:5432/aimbp"
# alembic offline 모드용 sync URL
SYNC_URL = ASYNC_URL.replace("postgresql+asyncpg://", "postgresql+psycopg2://")


def run_migrations_offline() -> None:
    context.configure(
        url=SYNC_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = ASYNC_URL
    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
