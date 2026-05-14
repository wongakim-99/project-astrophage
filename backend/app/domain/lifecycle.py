from collections.abc import Iterable
from datetime import UTC, datetime
from enum import StrEnum
from typing import Protocol


class LifecycleState(StrEnum):
    """최근 에너지와 비활성 기간에서 계산되는 항성 생애주기."""

    MAIN_SEQUENCE = "main_sequence"
    YELLOW_DWARF = "yellow_dwarf"
    RED_GIANT = "red_giant"
    WHITE_DWARF = "white_dwarf"
    DARK_MATTER = "dark_matter"


class LifecycleEvent(Protocol):
    """생애주기 계산에 필요한 이벤트 필드만 표현한다."""

    is_valid: bool
    energy_value: float
    started_at: datetime


ENERGY_THRESHOLD_ACTIVE = 3.0
ENERGY_THRESHOLD_NORMAL = 1.0
DAYS_RED_GIANT_START = 60
DAYS_WHITE_DWARF_START = 90
DAYS_DARK_MATTER_START = 180


def compute_lifecycle(
    recent_events: Iterable[LifecycleEvent],
    last_valid_event: LifecycleEvent | None,
) -> tuple[LifecycleState, float]:
    """최근 이벤트와 마지막 유효 조회 시각에서 생애주기 상태와 에너지를 계산한다."""
    energy_score = sum(e.energy_value for e in recent_events if e.is_valid)
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


def _days_since(event: LifecycleEvent | None) -> float | None:
    if event is None:
        return None
    last = event.started_at
    if last.tzinfo is None:
        last = last.replace(tzinfo=UTC)
    return (datetime.now(UTC) - last).total_seconds() / 86400
