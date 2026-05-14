"""
테스트 fixture.

pgvector가 설치된 실제 PostgreSQL 인스턴스가 필요하다.
TEST_DATABASE_URL 환경변수를 설정하지 않으면 로컬 기본값을 사용한다.
각 테스트는 teardown 시 롤백되는 트랜잭션 안에서 실행된다.
"""

import os
import uuid
from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, patch

import pytest_asyncio
from dotenv import load_dotenv
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

load_dotenv()

from app.core.dependencies import get_current_user, get_session  # noqa: E402
from app.main import app  # noqa: E402
from app.models.base import Base  # noqa: E402
from app.models.galaxy import Galaxy  # noqa: E402, F401 — Base에 등록
from app.models.star import Star  # noqa: E402, F401
from app.models.user import User  # noqa: E402, F401
from app.models.view_event import ViewEvent  # noqa: E402, F401
from app.models.wormhole import Wormhole  # noqa: E402, F401

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
