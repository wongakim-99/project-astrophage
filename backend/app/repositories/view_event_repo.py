import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.view_event import ViewEvent


class ViewEventRepository:
    """생애주기 에너지 이벤트 저장소."""

    def __init__(self, session: AsyncSession) -> None:
        """
        Args:
            session: 현재 요청 또는 작업에서 공유하는 비동기 DB 세션.
        """
        self._session = session

    async def list_recent_by_star(self, star_id: uuid.UUID, days: int = 30) -> list[ViewEvent]:
        """
        실시간 생애주기 점수 계산에 쓰는 슬라이딩 윈도우 이벤트를 반환한다.

        Args:
            star_id: 이벤트를 조회할 Star UUID.
            days: 현재 시각부터 거슬러 올라갈 조회 기간(일). 기본값은 최근 30일이다.
        """
        since = datetime.now(UTC) - timedelta(days=days)
        result = await self._session.execute(
            select(ViewEvent)
            .where(ViewEvent.star_id == star_id, ViewEvent.started_at >= since)
            .order_by(ViewEvent.started_at.desc())
        )
        return list(result.scalars().all())

    async def get_last_valid(self, star_id: uuid.UUID) -> ViewEvent | None:
        """
        비활성 기간 기반 상태 전환에 쓰는 최신 유효 에너지 이벤트를 찾는다.

        Args:
            star_id: 최신 유효 이벤트를 찾을 Star UUID.
        """
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
        """
        Args:
            star_id: 이벤트가 기록될 대상 Star UUID.
            user_id: 조회 또는 편집 액션을 수행한 사용자 UUID.
            duration_seconds: 단순 조회에서 사용자가 머문 시간(초). Nova 이벤트는 0을 사용한다.
            is_valid: 생애주기 에너지 계산에 포함할 이벤트인지 여부.
            is_edit: 편집으로 발생한 이벤트인지 여부. 편집 이벤트는 서비스에서 더 큰 에너지를 받는다.
            energy_value: 생애주기 점수에 더할 에너지 가중치.
        """
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
