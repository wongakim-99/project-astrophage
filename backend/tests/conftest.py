"""
테스트 fixture.

pgvector가 설치된 실제 PostgreSQL 인스턴스가 필요하다.
TEST_DATABASE_URL 환경변수를 명시해야 하며, 로컬 test DB만 허용한다.
각 테스트는 teardown 시 롤백되는 트랜잭션 안에서 실행된다.
"""

import os
import uuid
from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, patch
from urllib.parse import urlparse

import pytest_asyncio
from dotenv import load_dotenv
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

load_dotenv()

RAW_DATABASE_URL = os.getenv("DATABASE_URL")
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/astrophage_app_placeholder",
)

from app.core.dependencies import get_current_user, get_session  # noqa: E402
from app.main import app  # noqa: E402
from app.models.base import Base  # noqa: E402
from app.models.galaxy import Galaxy  # noqa: E402, F401 — Base에 등록
from app.models.star import Star  # noqa: E402, F401
from app.models.user import User  # noqa: E402, F401
from app.models.view_event import ViewEvent  # noqa: E402, F401
from app.models.wormhole import Wormhole  # noqa: E402, F401

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")
DATABASE_URL = RAW_DATABASE_URL

FAKE_EMBEDDING = [0.01] * 1536


@pytest_asyncio.fixture(scope="session")
async def engine() -> AsyncGenerator[AsyncEngine, None]:
    test_database_url = _require_safe_test_database_url()
    _engine = create_async_engine(test_database_url, echo=False)
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield _engine
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await _engine.dispose()


def _require_safe_test_database_url() -> str:
    """
    테스트 fixture는 drop_all/create_all을 실행하므로 원격/dev/prod DB 연결을 막는다.

    허용 조건:
    - TEST_DATABASE_URL을 명시적으로 설정
    - DATABASE_URL과 다른 값
    - host가 localhost/127.0.0.1/::1
    - database name에 test 포함
    """
    if not TEST_DATABASE_URL:
        raise RuntimeError(
            "TEST_DATABASE_URL is required. Refusing to reset an implicit database."
        )

    if DATABASE_URL and TEST_DATABASE_URL == DATABASE_URL:
        raise RuntimeError(
            "TEST_DATABASE_URL must not equal DATABASE_URL. Refusing to reset the app DB."
        )

    parsed = urlparse(TEST_DATABASE_URL)
    host = parsed.hostname or ""
    database_name = parsed.path.rsplit("/", maxsplit=1)[-1]
    if host not in {"localhost", "127.0.0.1", "::1"}:
        raise RuntimeError(
            "TEST_DATABASE_URL must point to a local database. "
            f"Refusing remote host: {host or '<missing>'}."
        )

    if "test" not in database_name.lower():
        raise RuntimeError(
            "TEST_DATABASE_URL database name must contain 'test'. "
            f"Refusing database: {database_name or '<missing>'}."
        )

    return TEST_DATABASE_URL


@pytest_asyncio.fixture
async def session(engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    async with engine.connect() as conn:
        await conn.begin_nested()
        factory = async_sessionmaker(bind=conn, expire_on_commit=False, class_=AsyncSession)
        async with factory() as s:
            yield s
            await s.rollback()


@pytest_asyncio.fixture
async def client(session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """DB 세션과 OpenAI mock을 주입한 HTTP 테스트 클라이언트."""

    async def _override_session() -> AsyncGenerator[AsyncSession, None]:
        yield session

    app.dependency_overrides[get_session] = _override_session

    with patch(
        "app.adapters.openai_embedding_provider.OpenAIEmbeddingProvider.embed_text",
        new_callable=AsyncMock,
    ) as mock_embed:
        mock_embed.return_value = FAKE_EMBEDDING
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            yield c

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def auth_client(session: AsyncSession) -> AsyncGenerator[tuple[AsyncClient, User], None]:
    """테스트 사용자를 만들고 current_user로 주입한 인증 클라이언트."""
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

    with patch(
        "app.adapters.openai_embedding_provider.OpenAIEmbeddingProvider.embed_text",
        new_callable=AsyncMock,
    ) as mock_embed:
        mock_embed.return_value = FAKE_EMBEDDING
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            yield c, user

    app.dependency_overrides.clear()
