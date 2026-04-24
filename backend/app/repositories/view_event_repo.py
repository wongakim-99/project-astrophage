import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.view_event import ViewEvent


class ViewEventRepository:
    """생애주기 에너지 이벤트 저장소."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_recent_by_star(self, star_id: uuid.UUID, days: int = 30) -> list[ViewEvent]:
        """실시간 생애주기 점수 계산에 쓰는 슬라이딩 윈도우 이벤트를 반환한다."""
        since = datetime.now(UTC) - timedelta(days=days)
        result = await self._session.execute(
            select(ViewEvent)
            .where(ViewEvent.star_id == star_id, ViewEvent.started_at >= since)
            .order_by(ViewEvent.started_at.desc())
        )
        return list(result.scalars().all())

    async def get_last_valid(self, star_id: uuid.UUID) -> ViewEvent | None:
        """비활성 기간 기반 상태 전환에 쓰는 최신 유효 에너지 이벤트를 찾는다."""
        result = await self._session.execute(
            select(ViewEvent)
            .where(ViewEvent.star_id == star_id, ViewEvent.is_valid == True)  # noqa: E712
            .order_by(ViewEvent.started_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        star_id: uuid.UUID,
        user_id: uuid.UUID,
        duration_seconds: int,
        is_valid: bool,
        is_edit: bool,
        energy_value: float,
    ) -> ViewEvent:
        event = ViewEvent(
            star_id=star_id,
            user_id=user_id,
            duration_seconds=duration_seconds,
            is_valid=is_valid,
            is_edit=is_edit,
            energy_value=energy_value,
        )
        self._session.add(event)
        await self._session.flush()
        return event
