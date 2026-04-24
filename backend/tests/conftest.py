"""
Test fixtures.

Requires a real PostgreSQL instance with pgvector.
Set TEST_DATABASE_URL env var or it falls back to a local default.
Each test runs in a transaction that is rolled back on teardown.
"""

import os
import uuid
from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, patch

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.dependencies import get_current_user, get_session
from app.main import app
from app.models.base import Base
from app.models.galaxy import Galaxy  # noqa: F401 — register with Base
from app.models.star import Star  # noqa: F401
from app.models.user import User  # noqa: F401
from app.models.view_event import ViewEvent  # noqa: F401
from app.models.wormhole import Wormhole  # noqa: F401

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/astrophage_test",
)

FAKE_EMBEDDING = [0.01] * 1536


@pytest_asyncio.fixture(scope="session")
async def engine():
    _engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield _engine
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await _engine.dispose()


@pytest_asyncio.fixture
async def session(engine) -> AsyncGenerator[AsyncSession, None]:  # type: ignore[no-untyped-def]
    async with engine.connect() as conn:
        await conn.begin_nested()
        factory = async_sessionmaker(bind=conn, expire_on_commit=False, class_=AsyncSession)
        async with factory() as s:
            yield s
            await s.rollback()


@pytest_asyncio.fixture
async def client(session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """HTTP test client with DB session and OpenAI mock injected."""

    async def _override_session() -> AsyncGenerator[AsyncSession, None]:
        yield session

    app.dependency_overrides[get_session] = _override_session

    with patch("app.services.embedding.embed_text", new_callable=AsyncMock) as mock_embed:
        mock_embed.return_value = FAKE_EMBEDDING
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            yield c

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def auth_client(session: AsyncSession) -> AsyncGenerator[tuple[AsyncClient, User], None]:
    """Authenticated test client — creates a user and injects it as current_user."""
    from app.core.security import hash_password

    user = User(
        username=f"testuser_{uuid.uuid4().hex[:6]}",
        email=f"test_{uuid.uuid4().hex[:6]}@example.com",
        password_hash=hash_password("password123"),
    )
    session.add(user)
    await session.flush()

    async def _override_session() -> AsyncGenerator[AsyncSession, None]:
        yield session

    async def _override_user() -> User:
        return user

    app.dependency_overrides[get_session] = _override_session
    app.dependency_overrides[get_current_user] = _override_user

    with patch("app.services.embedding.embed_text", new_callable=AsyncMock) as mock_embed:
        mock_embed.return_value = FAKE_EMBEDDING
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            yield c, user

    app.dependency_overrides.clear()
