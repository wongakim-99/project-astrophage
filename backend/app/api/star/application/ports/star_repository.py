import uuid
from datetime import datetime
from typing import Protocol


class StarRecord(Protocol):
    """항성 유스케이스가 영속성 모델에서 필요로 하는 필드."""

    id: uuid.UUID
    user_id: uuid.UUID
    galaxy_id: uuid.UUID
    title: str
    slug: str
    content: str
    embedding: list[float]
    pos_x: float
    pos_y: float
    is_public: bool
    created_at: datetime
    updated_at: datetime


class StarRepositoryPort(Protocol):
    """항성 영속성 기능 포트."""

    async def get_by_id(self, star_id: uuid.UUID) -> StarRecord | None: ...

    async def get_by_user_and_slug(self, user_id: uuid.UUID, slug: str) -> StarRecord | None: ...

    async def get_public_by_username_slug(self, username: str, slug: str) -> StarRecord | None: ...

    async def list_by_galaxy(self, galaxy_id: uuid.UUID) -> list[StarRecord]: ...

    async def list_public(
        self, limit: int = 50, offset: int = 0
    ) -> list[tuple[StarRecord, str]]: ...

    async def find_similar_in_galaxy(
        self,
        galaxy_id: uuid.UUID,
        embedding: list[float],
        exclude_id: uuid.UUID | None = None,
        k: int = 5,
    ) -> list[tuple[StarRecord, float]]: ...

    async def create(
        self,
        user_id: uuid.UUID,
        galaxy_id: uuid.UUID,
        title: str,
        slug: str,
        content: str,
        embedding: list[float],
        pos_x: float,
        pos_y: float,
        is_public: bool = False,
    ) -> StarRecord: ...

    async def update(
        self,
        star: StarRecord,
        title: str | None = None,
        content: str | None = None,
        embedding: list[float] | None = None,
        galaxy_id: uuid.UUID | None = None,
    ) -> StarRecord: ...

    async def set_all_public_for_user(self, user_id: uuid.UUID, is_public: bool) -> None: ...

    async def update_visibility(self, star: StarRecord, is_public: bool) -> StarRecord: ...

    async def delete(self, star: StarRecord) -> None: ...
