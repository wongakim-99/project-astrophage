from datetime import UTC, datetime

from app.models.view_event import ViewEvent
from app.schemas.star import LifecycleState

ENERGY_THRESHOLD_ACTIVE = 3.0
ENERGY_THRESHOLD_NORMAL = 1.0
DAYS_RED_GIANT_START = 60
DAYS_WHITE_DWARF_START = 90
DAYS_DARK_MATTER_START = 180
# 직접 조회/편집 에너지의 25%를 유사 항성에 1-hop Nova로 전파한다.
NOVA_ENERGY_RATIO = 0.25


def compute_lifecycle(
    recent_events: list[ViewEvent],
    last_valid_event: ViewEvent | None,
) -> tuple[LifecycleState, float]:
    """
    최근 30일 이벤트와 마지막 유효 조회 시각을 기준으로
    (lifecycle_state, energy_score)를 반환한다.

    Args:
        recent_events: 에너지 점수에 반영할 최근 ViewEvent 목록.
        last_valid_event: 비활성 기간 계산에 사용할 최신 유효 ViewEvent. 없으면 None.
    """
    # 나중에 배치 job으로 바꾸더라도 repository 쿼리를 바꾸지 않도록
    # 생애주기 계산은 service 계층에 둔다.
    energy_score = sum(
        e.energy_value
        for e in recent_events
        if e.is_valid
    )

    days_inactive = _days_since(last_valid_event)

    if days_inactive is not None:
        if days_inactive >= DAYS_DARK_MATTER_START:
            return LifecycleState.DARK_MATTER, energy_score
        if days_inactive >= DAYS_WHITE_DWARF_START:
            return LifecycleState.WHITE_DWARF, energy_score
        if days_inactive >= DAYS_RED_GIANT_START:
            return LifecycleState.RED_GIANT, energy_score

    if energy_score >= ENERGY_THRESHOLD_ACTIVE:
        return LifecycleState.MAIN_SEQUENCE, energy_score
    if energy_score >= ENERGY_THRESHOLD_NORMAL:
        return LifecycleState.YELLOW_DWARF, energy_score

    return LifecycleState.YELLOW_DWARF, energy_score


def _days_since(event: ViewEvent | None) -> float | None:
    """
    과거 row가 naive datetime이어도 UTC 기준 경과 일수를 반환한다.

    Args:
        event: 경과 일수를 계산할 ViewEvent. 없으면 None을 반환한다.
    """
    if event is None:
        return None
    last = event.started_at
    if last.tzinfo is None:
        last = last.replace(tzinfo=UTC)
    return (datetime.now(UTC) - last).total_seconds() / 86400
