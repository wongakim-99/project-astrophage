import uuid

from app.application.galaxy_dto import GalaxyDetails
from app.domain.galaxy.rules import default_galaxy_color
from app.models.galaxy import Galaxy
from app.ports.galaxy_repository import GalaxyRepositoryPort
from app.ports.unit_of_work import UnitOfWorkPort


class GalaxyUseCaseError(Exception):
    """라우터가 HTTP 오류로 변환할 은하 유스케이스 예외."""

    pass


class GalaxyUseCases:
    """사용자 소유 은하 CRUD 유스케이스의 트랜잭션 흐름을 조율한다."""

    def __init__(self, unit_of_work: UnitOfWorkPort, galaxy_repo: GalaxyRepositoryPort) -> None:
        """
        Args:
            unit_of_work: 은하 조회/변경을 확정할 트랜잭션 포트.
        """
        self._uow = unit_of_work
        self._repo = galaxy_repo

    async def list_galaxies(self, user_id: uuid.UUID) -> list[GalaxyDetails]:
        """
        탐색 UI에 필요한 가벼운 항성 수와 함께 은하 목록을 반환한다.

        Args:
            user_id: 은하 목록을 가져올 소유자 UUID.
        """
        galaxies = await self._repo.list_by_user(user_id)
        result: list[GalaxyDetails] = []
        for galaxy in galaxies:
            count = await self._repo.count_stars(galaxy.id)
            result.append(self._to_details(galaxy, star_count=count))
        return result

    async def create_galaxy(
        self, user_id: uuid.UUID, name: str, slug: str, color: str | None
    ) -> GalaxyDetails:
        """
        사용자 범위 slug 중복을 확인하고 새 은하를 생성한다.

        Args:
            user_id: 새 은하를 소유할 사용자 UUID.
            name: 화면에 표시할 은하 이름.
            slug: 사용자 범위에서 유일해야 하는 URL용 은하 식별자.
            color: 클라이언트가 지정한 7자리 hex 색상. None이면 팔레트에서 자동 선택한다.
        """
        if await self._repo.get_by_user_and_slug(user_id, slug):
            raise GalaxyUseCaseError(f"Galaxy slug '{slug}' already exists")

        if color is None:
            existing = await self._repo.list_by_user(user_id)
            color = default_galaxy_color(len(existing))

        galaxy = await self._repo.create(user_id=user_id, name=name, slug=slug, color=color)
        await self._uow.commit()
        return self._to_details(galaxy)

    async def update_galaxy(
        self, user_id: uuid.UUID, galaxy_id: uuid.UUID, name: str | None, color: str | None
    ) -> GalaxyDetails:
        """
        소유권을 확인한 뒤 은하의 표시 이름과 색상을 수정한다.

        Args:
            user_id: 변경을 요청한 사용자 UUID.
            galaxy_id: 수정할 Galaxy UUID.
            name: 새 은하 이름. None이면 기존 값을 유지한다.
            color: 새 7자리 hex 색상. None이면 기존 값을 유지한다.
        """
        galaxy = await self._get_owned(user_id, galaxy_id)
        galaxy = await self._repo.update(galaxy, name=name, color=color)
        await self._uow.commit()
        return self._to_details(galaxy)

    async def delete_galaxy(self, user_id: uuid.UUID, galaxy_id: uuid.UUID) -> None:
        """
        소유권을 확인한 뒤 은하를 삭제한다.

        Args:
            user_id: 삭제를 요청한 사용자 UUID.
            galaxy_id: 삭제할 Galaxy UUID.
        """
        galaxy = await self._get_owned(user_id, galaxy_id)
        await self._repo.delete(galaxy)
        await self._uow.commit()

    async def _get_owned(self, user_id: uuid.UUID, galaxy_id: uuid.UUID) -> Galaxy:
        """
        은하 변경 전에 개인 우주 소유권을 검증한다.

        Args:
            user_id: 소유권을 확인할 사용자 UUID.
            galaxy_id: 소유 여부를 확인할 Galaxy UUID.
        """
        galaxy = await self._repo.get_by_id(galaxy_id)
        if galaxy is None or galaxy.user_id != user_id:
            raise GalaxyUseCaseError("Galaxy not found")
        return galaxy

    def _to_details(self, galaxy: Galaxy, star_count: int = 0) -> GalaxyDetails:
        return GalaxyDetails(
            id=galaxy.id,
            name=galaxy.name,
            slug=galaxy.slug,
            color=galaxy.color,
            star_count=star_count,
        )
