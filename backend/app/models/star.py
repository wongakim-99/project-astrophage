from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from pgvector.sqlalchemy import Vector
from sqlalchemy import Boolean, Float, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, new_uuid

if TYPE_CHECKING:
    from app.models.galaxy import Galaxy
    from app.models.user import User
    from app.models.view_event import ViewEvent

EMBEDDING_DIM = 1536


class Star(Base, TimestampMixin):
    """임베딩, 고정 2D 좌표, 공개 여부를 가진 지식 포스트."""

    __tablename__ = "stars"
    # 공개 URL은 /{username}/stars/{slug}이므로 슬러그는 사용자별로만 유일하다.
    __table_args__ = (UniqueConstraint("user_id", "slug", name="uq_star_user_slug"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=new_uuid)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    galaxy_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("galaxies.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False, default="")
    # 생성/수정 시 저장하고, GET 경로에서는 이 값을 재사용한다. 조회 중 OpenAI 호출 금지.
    embedding: Mapped[list[float]] = mapped_column(Vector(EMBEDDING_DIM), nullable=False)
    # 좌표는 항성 생성 시 정해지며, 자동 UMAP식 재계산으로 덮어쓰면 안 된다.
    pos_x: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    pos_y: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    # 기본값은 비공개다. 공개 엔드포인트는 반드시 이 플래그로 필터링해야 한다.
    is_public: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    owner: Mapped[User] = relationship(back_populates="stars", lazy="noload")
    galaxy: Mapped[Galaxy] = relationship(back_populates="stars", lazy="noload")
    view_events: Mapped[list[ViewEvent]] = relationship(back_populates="star", lazy="noload")
