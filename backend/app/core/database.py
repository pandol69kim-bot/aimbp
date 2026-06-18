from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from typing import AsyncGenerator

from app.core.config import settings


class Base(DeclarativeBase):
    pass


engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    await _run_migrations()
    await _seed_vocal_library()


async def _run_migrations() -> None:
    import subprocess
    import sys
    import logging as _log
    logger = _log.getLogger(__name__)
    result = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd="/app",
        capture_output=True,
        text=True,
    )
    for line in (result.stdout + result.stderr).splitlines():
        if line.strip():
            logger.info(f"[alembic] {line}")
    if result.returncode != 0:
        logger.warning("Alembic migration failed, falling back to create_all")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)


async def _seed_vocal_library() -> None:
    from app.models.vocal import VocalLibrary
    from app.services.vocal import SAMPLE_VOCAL_LIBRARY
    from sqlalchemy import select

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(VocalLibrary).limit(1))
        if result.scalar_one_or_none():
            return
        for item in SAMPLE_VOCAL_LIBRARY:
            session.add(VocalLibrary(**item))
        await session.commit()
