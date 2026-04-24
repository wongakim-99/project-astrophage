from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, new_uuid

if TYPE_CHECKING:
    from app.models.star import Star
    from app.models.user import User

GALAXY_COLOR_PALETTE = [
    "#4A9EFF",
    "#FF7043",
    "#66BB6A",
    "#AB47BC",
    "#FFA726",
    "#26C6DA",
    "#EC407A",
    "#8D6E63",
]


class Galaxy(Base, TimestampMixin):
    __tablename__ = "galaxies"
    __table_args__ = (UniqueConstraint("user_id", "slug", name="uq_galaxy_user_slug"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=new_uuid)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), nullable=False)
    color: Mapped[str] = mapped_column(String(7), nullable=False)

    owner: Mapped[User] = relationship(back_populates="galaxies", lazy="noload")
    stars: Mapped[list[Star]] = relationship(back_populates="galaxy", lazy="noload")
