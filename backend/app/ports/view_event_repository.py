import uuid
from typing import Protocol

from app.models.view_event import ViewEvent


class ViewEventRepositoryPort(Protocol):
    """조회/편집 이벤트 영속성 기능 포트."""

    async def list_recent_by_star(self, star_id: uuid.UUID, days: int = 30) -> list[ViewEvent]: ...

    async def get_last_valid(self, star_id: uuid.UUID) -> ViewEvent | None: ...

    async def list_recent_by_stars(
        self, star_ids: list[uuid.UUID], days: int = 30
    ) -> dict[uuid.UUID, list[ViewEvent]]: ...

    async def get_last_valids(
        self, star_ids: list[uuid.UUID]
    ) -> dict[uuid.UUID, ViewEvent | None]: ...

    async def create(
        self,
        star_id: uuid.UUID,
        user_id: uuid.UUID,
        duration_seconds: int,
        is_valid: bool,
        is_edit: bool,
        energy_value: float,
    ) -> ViewEvent: ...
