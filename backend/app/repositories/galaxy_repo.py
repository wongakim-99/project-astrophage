import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.galaxy import Galaxy
from app.models.star import Star


class GalaxyRepository:
    """사용자 소유 Galaxy에 대한 SQLAlchemy 쿼리 모음."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, galaxy_id: uuid.UUID) -> Galaxy | None:
        result = await self._session.execute(select(Galaxy).where(Galaxy.id == galaxy_id))
        return result.scalar_one_or_none()

    async def get_by_user_and_slug(self, user_id: uuid.UUID, slug: str) -> Galaxy | None:
        result = await self._session.execute(
            select(Galaxy).where(Galaxy.user_id == user_id, Galaxy.slug == slug)
        )
        return result.scalar_one_or_none()

    async def list_by_user(self, user_id: uuid.UUID) -> list[Galaxy]:
        result = await self._session.execute(
            select(Galaxy).where(Galaxy.user_id == user_id).order_by(Galaxy.created_at)
        )
        return list(result.scalars().all())

    async def count_stars(self, galaxy_id: uuid.UUID) -> int:
        """목록 응답용 항성 수를 전체 row 로딩 없이 계산한다."""
        result = await self._session.execute(
            select(func.count()).where(Star.galaxy_id == galaxy_id)
        )
        return result.scalar_one()

    async def create(self, user_id: uuid.UUID, name: str, slug: str, color: str) -> Galaxy:
        galaxy = Galaxy(user_id=user_id, name=name, slug=slug, color=color)
        self._session.add(galaxy)
        await self._session.flush()
        await self._session.refresh(galaxy)
        return galaxy

    async def update(self, galaxy: Galaxy, name: str | None, color: str | None) -> Galaxy:
        if name is not None:
            galaxy.name = name
        if color is not None:
            galaxy.color = color
        await self._session.flush()
        await self._session.refresh(galaxy)
        return galaxy

    async def delete(self, galaxy: Galaxy) -> None:
        await self._session.delete(galaxy)
        await self._session.flush()
