from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, new_uuid

if TYPE_CHECKING:
    from app.models.galaxy import Galaxy
    from app.models.star import Star


class User(Base, TimestampMixin):
    """애플리케이션 계정. 은하와 항성은 이 소유자를 기준으로 격리된다."""

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=new_uuid)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_universe_public: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # noload는 async 요청 처리 중 실수로 relationship 접근이 암묵적 IO를 일으키는 것을 막는다.
    # 필요한 데이터는 repository가 명시적으로 가져온다.
    galaxies: Mapped[list[Galaxy]] = relationship(back_populates="owner", lazy="noload")
    stars: Mapped[list[Star]] = relationship(back_populates="owner", lazy="noload")
