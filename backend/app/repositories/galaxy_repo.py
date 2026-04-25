import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.galaxy import Galaxy
from app.models.star import Star


class GalaxyRepository:
    """사용자 소유 Galaxy에 대한 SQLAlchemy 쿼리 모음."""

    def __init__(self, session: AsyncSession) -> None:
        """
        Args:
            session: 현재 요청 또는 작업에서 공유하는 비동기 DB 세션.
        """
        self._session = session

    async def get_by_id(self, galaxy_id: uuid.UUID) -> Galaxy | None:
        """
        Args:
            galaxy_id: 조회할 Galaxy의 기본키 UUID.
        """
        result = await self._session.execute(select(Galaxy).where(Galaxy.id == galaxy_id))
        return result.scalar_one_or_none()

    async def get_by_user_and_slug(self, user_id: uuid.UUID, slug: str) -> Galaxy | None:
        """
        Args:
            user_id: Galaxy를 소유한 사용자 UUID. 사용자별 slug 유일성 범위를 정한다.
            slug: 사용자의 개인 우주 안에서 Galaxy를 식별하는 URL용 문자열.
        """
        result = await self._session.execute(
            select(Galaxy).where(Galaxy.user_id == user_id, Galaxy.slug == slug)
        )
        return result.scalar_one_or_none()

    async def list_by_user(self, user_id: uuid.UUID) -> list[Galaxy]:
        """
        Args:
            user_id: 목록으로 가져올 Galaxy들의 소유자 UUID.
        """
        result = await self._session.execute(
            select(Galaxy).where(Galaxy.user_id == user_id).order_by(Galaxy.created_at)
        )
        return list(result.scalars().all())

    async def count_stars(self, galaxy_id: uuid.UUID) -> int:
        """
        목록 응답용 항성 수를 전체 row 로딩 없이 계산한다.

        Args:
            galaxy_id: 항성 수를 계산할 Galaxy UUID.
        """
        result = await self._session.execute(
            select(func.count()).where(Star.galaxy_id == galaxy_id)
        )
        return result.scalar_one()

    async def create(self, user_id: uuid.UUID, name: str, slug: str, color: str) -> Galaxy:
        """
        Args:
            user_id: 새 Galaxy를 소유할 사용자 UUID.
            name: 화면에 표시할 Galaxy 이름.
            slug: 사용자별로 유일해야 하는 URL용 Galaxy 식별자.
            color: 탐색 UI에서 Galaxy를 구분할 7자리 hex 색상 문자열.
        """
        galaxy = Galaxy(user_id=user_id, name=name, slug=slug, color=color)
        self._session.add(galaxy)
        await self._session.flush()
        await self._session.refresh(galaxy)
        return galaxy

    async def update(self, galaxy: Galaxy, name: str | None, color: str | None) -> Galaxy:
        """
        Args:
            galaxy: 수정할 영속 상태의 Galaxy 모델 인스턴스.
            name: 새 Galaxy 이름. None이면 기존 값을 유지한다.
            color: 새 7자리 hex 색상 문자열. None이면 기존 값을 유지한다.
        """
        if name is not None:
            galaxy.name = name
        if color is not None:
            galaxy.color = color
        await self._session.flush()
        await self._session.refresh(galaxy)
        return galaxy

    async def delete(self, galaxy: Galaxy) -> None:
        """
        Args:
            galaxy: 삭제할 영속 상태의 Galaxy 모델 인스턴스.
        """
        await self._session.delete(galaxy)
        await self._session.flush()
