import uuid
from typing import Protocol


class GalaxyRecord(Protocol):
    """은하 유스케이스가 영속성 모델에서 필요로 하는 필드."""

    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    slug: str
    color: str


class GalaxyRepositoryPort(Protocol):
    """은하 영속성 기능 포트."""

    async def get_by_id(self, galaxy_id: uuid.UUID) -> GalaxyRecord | None: ...

    async def get_by_user_and_slug(self, user_id: uuid.UUID, slug: str) -> GalaxyRecord | None: ...

    async def list_by_user(self, user_id: uuid.UUID) -> list[GalaxyRecord]: ...

    async def count_stars(self, galaxy_id: uuid.UUID) -> int: ...

    async def create(self, user_id: uuid.UUID, name: str, slug: str, color: str) -> GalaxyRecord: ...

    async def update(
        self, galaxy: GalaxyRecord, name: str | None, color: str | None
    ) -> GalaxyRecord: ...

    async def delete(self, galaxy: GalaxyRecord) -> None: ...
