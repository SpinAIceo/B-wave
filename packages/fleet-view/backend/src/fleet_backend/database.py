from __future__ import annotations

import os

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

_raw_url = os.environ.get("DATABASE_URL", "sqlite+aiosqlite:///./bwave_fleet.db")

# Railway injects postgres:// or postgresql:// — upgrade to asyncpg scheme
if _raw_url.startswith("postgres://"):
    DATABASE_URL = _raw_url.replace("postgres://", "postgresql+asyncpg://", 1)
elif _raw_url.startswith("postgresql://"):
    DATABASE_URL = _raw_url.replace("postgresql://", "postgresql+asyncpg://", 1)
else:
    DATABASE_URL = _raw_url

_is_sqlite = DATABASE_URL.startswith("sqlite")

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    # SQLite needs check_same_thread=False; asyncpg doesn't use this kwarg
    **({"connect_args": {"check_same_thread": False}} if _is_sqlite else {}),
)

AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def init_db() -> None:
    from . import orm  # noqa: F401 — registers ORM models with Base

    import asyncio
    from pathlib import Path

    from alembic import command
    from alembic.config import Config as AlembicConfig

    # Locate alembic.ini relative to this package (../../../alembic.ini from src/)
    _ini = Path(__file__).parent.parent.parent.parent / "alembic.ini"
    alembic_cfg = AlembicConfig(str(_ini))
    # Always override the URL so the right DB is targeted at runtime
    alembic_cfg.set_main_option("sqlalchemy.url", DATABASE_URL)

    await asyncio.get_event_loop().run_in_executor(
        None, lambda: command.upgrade(alembic_cfg, "head")
    )


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
