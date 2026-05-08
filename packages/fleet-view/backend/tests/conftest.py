import asyncio

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from fleet_backend import orm  # noqa: F401 — registers ORM models with Base
from fleet_backend.auth import UserInDB, Role, get_current_user
from fleet_backend.database import Base, get_db
from fleet_backend.main import app
from fleet_backend.store import seed_initial_data

_TEST_DB_URL = "sqlite+aiosqlite:///:memory:"
_engine = create_async_engine(_TEST_DB_URL, connect_args={"check_same_thread": False})
_SessionLocal = async_sessionmaker(_engine, expire_on_commit=False)

_ADMIN_USER = UserInDB(username="test-admin", hashed_password="", role=Role.ADMIN)


async def _bootstrap() -> None:
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with _SessionLocal() as session:
        await seed_initial_data(session)


# Run synchronously at import time so the DB is ready before any test module loads
asyncio.run(_bootstrap())


async def _override_get_db():
    async with _SessionLocal() as session:
        yield session


async def _override_get_current_user():
    return _ADMIN_USER


# Override dependencies for all tests
app.dependency_overrides[get_db] = _override_get_db
app.dependency_overrides[get_current_user] = _override_get_current_user
