import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Alembic이 메타데이터를 찾을 때 사용하는 공통 SQLAlchemy 선언형 base."""

    pass


class TimestampMixin:
    """소유자 단위 콘텐츠 테이블에서 공통으로 쓰는 생성/수정 시각 컬럼."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )


def new_uuid() -> uuid.UUID:
    return uuid.uuid4()
