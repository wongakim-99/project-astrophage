"""pgvector 확장을 포함한 초기 스키마

Revision ID: 001
Revises:
Create Date: 2026-04-24
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # VECTOR(1536) 임베딩 컬럼을 만들기 전에 pgvector 확장이 필요하다.
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "users",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("username", sa.String(50), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_users_username", "users", ["username"], unique=True)
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "galaxies",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("slug", sa.String(100), nullable=False),
        sa.Column("color", sa.String(7), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "slug", name="uq_galaxy_user_slug"),
    )
    op.create_index("ix_galaxies_user_id", "galaxies", ["user_id"])

    op.create_table(
        "stars",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("galaxy_id", sa.UUID(), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("slug", sa.String(200), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        # 조회와 공개 페이지가 OpenAI를 호출하지 않도록 임베딩을 저장한다.
        sa.Column("embedding", Vector(1536), nullable=False),
        # 최초 2D 배치를 직접 저장하고 UX를 위해 안정적으로 유지한다.
        sa.Column("pos_x", sa.Float(), nullable=False),
        sa.Column("pos_y", sa.Float(), nullable=False),
        # 항성은 비공개로 시작하며, 공개하려면 소유자의 명시적 액션이 필요하다.
        sa.Column("is_public", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["galaxy_id"], ["galaxies.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "slug", name="uq_star_user_slug"),
    )
    op.create_index("ix_stars_user_id", "stars", ["user_id"])
    op.create_index("ix_stars_galaxy_id", "stars", ["galaxy_id"])

    op.create_table(
        "view_events",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("star_id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("duration_seconds", sa.Integer(), nullable=False),
        # 유효 이벤트는 생애주기 에너지를 만든다. 짧은 체류 기록은 상태에 영향 없이
        # 나중에 분석용으로 사용할 수 있다.
        sa.Column("is_valid", sa.Boolean(), nullable=False),
        sa.Column("is_edit", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("energy_value", sa.Float(), nullable=False, server_default="1.0"),
        sa.ForeignKeyConstraint(["star_id"], ["stars.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_view_events_star_id", "view_events", ["star_id"])
    op.create_index("ix_view_events_user_id", "view_events", ["user_id"])
    op.create_index("ix_view_events_started_at", "view_events", ["started_at"])

    op.create_table(
        "wormholes",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("star_a_id", sa.UUID(), nullable=False),
        sa.Column("star_b_id", sa.UUID(), nullable=False),
        sa.Column("similarity", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["star_a_id"], ["stars.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["star_b_id"], ["stars.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("star_a_id", "star_b_id", name="uq_wormhole_pair"),
    )
    op.create_index("ix_wormholes_star_a_id", "wormholes", ["star_a_id"])
    op.create_index("ix_wormholes_star_b_id", "wormholes", ["star_b_id"])


def downgrade() -> None:
    op.drop_table("wormholes")
    op.drop_table("view_events")
    op.drop_table("stars")
    op.drop_table("galaxies")
    op.drop_table("users")
    op.execute("DROP EXTENSION IF EXISTS vector")
