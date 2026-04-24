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
    is_valid: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_edit: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    energy_value: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)

    star: Mapped[Star] = relationship(back_populates="view_events", lazy="noload")
