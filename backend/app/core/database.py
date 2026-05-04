from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

# 앱 전체에서 하나의 async engine을 공유한다. pool_pre_ping은 Railway 같은
# 장시간 유휴 연결이 끊겼을 때 재연결을 안정적으로 처리하게 해준다.
engine = create_async_engine(
    settings.database_url,
    echo=settings.app_env == "development",
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

async_session_factory = async_sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """요청마다 하나의 SQLAlchemy 세션을 제공하는 FastAPI 의존성."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
