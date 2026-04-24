import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import settings
from app.models.base import Base
# Alembic autogenerate가 Base.metadata를 통해 모든 테이블을 볼 수 있도록 모델을 import한다.
from app.models.galaxy import Galaxy  # noqa: F401
from app.models.star import Star  # noqa: F401
from app.models.user import User  # noqa: F401
from app.models.view_event import ViewEvent  # noqa: F401
from app.models.wormhole import Wormhole  # noqa: F401

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """async DB 연결을 열지 않고 SQL만 생성한다."""
    context.configure(
        url=settings.database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):  # type: ignore[no-untyped-def]
    """Alembic의 동기 migration API를 async engine 연결 위에서 실행한다."""
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """설정된 async PostgreSQL 데이터베이스에 migration을 적용한다."""
    connectable = create_async_engine(settings.database_url)
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
