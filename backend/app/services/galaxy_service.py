import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.galaxy import GALAXY_COLOR_PALETTE, Galaxy
from app.repositories.galaxy_repo import GalaxyRepository


class GalaxyError(Exception):
    """라우터가 HTTP 오류로 변환할 은하 도메인 예외."""

    pass


class GalaxyService:
    """사용자 소유 은하 CRUD의 비즈니스 규칙."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._repo = GalaxyRepository(session)

    async def list_galaxies(self, user_id: uuid.UUID) -> list[dict]:  # type: ignore[type-arg]
        """탐색 UI에 필요한 가벼운 항성 수와 함께 은하 목록을 반환한다."""
        galaxies = await self._repo.list_by_user(user_id)
        result = []
        for g in galaxies:
            count = await self._repo.count_stars(g.id)
            result.append({**g.__dict__, "star_count": count})
        return result

    async def create_galaxy(
        self, user_id: uuid.UUID, name: str, slug: str, color: str | None
    ) -> Galaxy:
        if await self._repo.get_by_user_and_slug(user_id, slug):
            raise GalaxyError(f"Galaxy slug '{slug}' already exists")

        if color is None:
            # 결정적인 팔레트 순환으로 생성 로직은 단순하게 유지하면서
            # 인접한 은하의 기본 색상이 서로 구분되게 한다.
            existing = await self._repo.list_by_user(user_id)
            color = GALAXY_COLOR_PALETTE[len(existing) % len(GALAXY_COLOR_PALETTE)]

        galaxy = await self._repo.create(user_id=user_id, name=name, slug=slug, color=color)
        await self._session.commit()
        return galaxy

    async def update_galaxy(
        self, user_id: uuid.UUID, galaxy_id: uuid.UUID, name: str | None, color: str | None
    ) -> Galaxy:
        galaxy = await self._get_owned(user_id, galaxy_id)
        galaxy = await self._repo.update(galaxy, name=name, color=color)
        await self._session.commit()
        return galaxy

    async def delete_galaxy(self, user_id: uuid.UUID, galaxy_id: uuid.UUID) -> None:
        galaxy = await self._get_owned(user_id, galaxy_id)
        await self._repo.delete(galaxy)
        await self._session.commit()

    async def _get_owned(self, user_id: uuid.UUID, galaxy_id: uuid.UUID) -> Galaxy:
        """은하 변경 전에 개인 우주 소유권을 검증한다."""
        galaxy = await self._repo.get_by_id(galaxy_id)
        if galaxy is None or galaxy.user_id != user_id:
            raise GalaxyError("Galaxy not found")
        return galaxy
