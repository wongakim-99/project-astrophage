import uuid
from datetime import datetime
from typing import Protocol


class ViewEventRecord(Protocol):
    """생애주기 계산에 필요한 조회/편집 이벤트 필드."""

    id: uuid.UUID
    star_id: uuid.UUID
    user_id: uuid.UUID
    started_at: datetime
    duration_seconds: int
    is_valid: bool
    is_edit: bool
    energy_value: float


class ViewEventRepositoryPort(Protocol):
    """조회/편집 이벤트 영속성 기능 포트."""

    async def list_recent_by_star(
        self, star_id: uuid.UUID, days: int = 30
    ) -> list[ViewEventRecord]: ...

    async def get_last_valid(self, star_id: uuid.UUID) -> ViewEventRecord | None: ...

    async def list_recent_by_stars(
        self, star_ids: list[uuid.UUID], days: int = 30
    ) -> dict[uuid.UUID, list[ViewEventRecord]]: ...

    async def get_last_valids(
        self, star_ids: list[uuid.UUID]
    ) -> dict[uuid.UUID, ViewEventRecord | None]: ...

    async def create(
        self,
        star_id: uuid.UUID,
        user_id: uuid.UUID,
        duration_seconds: int,
        is_valid: bool,
        is_edit: bool,
        energy_value: float,
    ) -> ViewEventRecord: ...
