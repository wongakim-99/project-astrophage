import uuid
from typing import Protocol

from app.models.star import Star


class StarRepositoryPort(Protocol):
    """항성 영속성 기능 포트."""

    async def get_by_id(self, star_id: uuid.UUID) -> Star | None: ...

    async def get_by_user_and_slug(self, user_id: uuid.UUID, slug: str) -> Star | None: ...

    async def get_public_by_username_slug(self, username: str, slug: str) -> Star | None: ...

    async def list_by_galaxy(self, galaxy_id: uuid.UUID) -> list[Star]: ...

    async def list_public(self, limit: int = 50, offset: int = 0) -> list[tuple[Star, str]]: ...

    async def find_similar_in_galaxy(
        self,
        galaxy_id: uuid.UUID,
        embedding: list[float],
        exclude_id: uuid.UUID | None = None,
        k: int = 5,
    ) -> list[tuple[Star, float]]: ...

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
    ) -> Star: ...

    async def update(
        self,
        star: Star,
        title: str | None = None,
        content: str | None = None,
        embedding: list[float] | None = None,
        galaxy_id: uuid.UUID | None = None,
    ) -> Star: ...

    async def set_all_public_for_user(self, user_id: uuid.UUID, is_public: bool) -> None: ...

    async def update_visibility(self, star: Star, is_public: bool) -> Star: ...

    async def delete(self, star: Star) -> None: ...
