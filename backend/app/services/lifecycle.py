from datetime import UTC, datetime

from app.models.view_event import ViewEvent
from app.schemas.star import LifecycleState

ENERGY_THRESHOLD_ACTIVE = 3.0
ENERGY_THRESHOLD_NORMAL = 1.0
DAYS_RED_GIANT_START = 60
DAYS_WHITE_DWARF_START = 90
DAYS_DARK_MATTER_START = 180
NOVA_ENERGY_RATIO = 0.25  # 25% of direct view energy propagated to similar stars


def compute_lifecycle(
    recent_events: list[ViewEvent],
    last_valid_event: ViewEvent | None,
) -> tuple[LifecycleState, float]:
    """
    Returns (lifecycle_state, energy_score) based on recent 30-day events
    and the timestamp of the last valid view.
    """
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
    if event is None:
        return None
    last = event.started_at
    if last.tzinfo is None:
        last = last.replace(tzinfo=UTC)
    return (datetime.now(UTC) - last).total_seconds() / 86400
