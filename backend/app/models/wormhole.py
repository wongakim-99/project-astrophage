"""Wormhole model — Phase 2. Schema defined here so Alembic can create the table,
but no service/router logic is implemented yet."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, Float, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, new_uuid


class Wormhole(Base):
    __tablename__ = "wormholes"
    __table_args__ = (UniqueConstraint("star_a_id", "star_b_id", name="uq_wormhole_pair"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=new_uuid)
    star_a_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("stars.id", ondelete="CASCADE"), nullable=False, index=True)
    star_b_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("stars.id", ondelete="CASCADE"), nullable=False, index=True)
    similarity: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
