from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, new_uuid

if TYPE_CHECKING:
    from app.models.star import Star

VALID_DWELL_SECONDS = 30


class ViewEvent(Base):
    """생애주기 상태의 에너지 원천. 유효 체류, 편집, Nova 이벤트를 저장한다."""

    __tablename__ = "view_events"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=new_uuid)
    star_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("stars.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
        index=True,
    )
    duration_seconds: Mapped[int] = mapped_column(nullable=False, default=0)
    # 30초 이상 체류, 편집, Nova 전파 에너지 기록이면 True다.
    is_valid: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    # 편집 이벤트는 lifecycle 서비스에서 더 강한 직접 에너지로 계산된다.
    is_edit: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    # Nova 전파처럼 소수점 가중치를 저장하면서도 lifecycle 집계 쿼리 구조를 유지한다.
    energy_value: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)

    star: Mapped[Star] = relationship(back_populates="view_events", lazy="noload")
