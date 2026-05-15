import contextvars
import re
import time
from collections.abc import AsyncGenerator
from typing import Any

from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.common.config import settings

# 요청 범위 쿼리 타이밍 로그. 미들웨어가 요청 시작 시 빈 리스트로 설정하고,
# 이벤트 리스너가 쿼리마다 (sql_summary, elapsed_ms) 를 append한다.
request_query_log: contextvars.ContextVar[list[tuple[str, float]] | None] = (
    contextvars.ContextVar("request_query_log", default=None)
)

# 앱 전체에서 하나의 async engine을 공유한다. pool_pre_ping은 Railway 같은
# 장시간 유휴 연결이 끊겼을 때 재연결을 안정적으로 처리하게 해준다.
engine = create_async_engine(
    settings.database_url,
    echo=False,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

if settings.app_env == "development":
    @event.listens_for(engine.sync_engine, "before_cursor_execute")
    def _before_execute(
        conn: Any,
        cursor: object,
        statement: str,
        parameters: object,
        context: object,
        executemany: bool,
    ) -> None:
        conn.info["_t"] = time.perf_counter()

    @event.listens_for(engine.sync_engine, "after_cursor_execute")
    def _after_execute(
        conn: Any,
        cursor: object,
        statement: str,
        parameters: object,
        context: object,
        executemany: bool,
    ) -> None:
        info = conn.info
        elapsed_ms = (time.perf_counter() - info.pop("_t", time.perf_counter())) * 1000
        log = request_query_log.get(None)
        if log is not None:
            log.append((_sql_summary(statement), elapsed_ms))


def _sql_summary(sql: str) -> str:
    line = re.sub(r"\s+", " ", sql.strip())
    return line[:90] + ("…" if len(line) > 90 else "")

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
            t = time.perf_counter()
            await session.commit()
            if settings.app_env == "development":
                elapsed_ms = (time.perf_counter() - t) * 1000
                log = request_query_log.get(None)
                if log is not None:
                    log.append(("COMMIT", elapsed_ms))
        except Exception:
            await session.rollback()
            raise
