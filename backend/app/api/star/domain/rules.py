from dataclasses import dataclass

VALID_DWELL_SECONDS = 30
NOVA_ENERGY_RATIO = 0.25


@dataclass(frozen=True)
class DirectViewEnergy:
    """직접 조회/편집 이벤트가 생애주기에 주는 에너지 판정."""

    is_valid: bool
    value: float


def embedding_source(title: str, content: str) -> str:
    """항성 의미 벡터 입력으로 사용할 도메인 텍스트를 만든다."""
    return f"{title}\n{content}"


def initial_star_visibility(is_universe_public: bool) -> bool:
    """공개 우주에 새로 생기는 항성은 즉시 공개된다."""
    return is_universe_public


def direct_view_energy(duration_seconds: int, is_edit: bool) -> DirectViewEnergy:
    """체류/편집 이벤트의 유효 여부와 직접 에너지 값을 계산한다."""
    if is_edit:
        return DirectViewEnergy(is_valid=True, value=2.0)
    return DirectViewEnergy(
        is_valid=duration_seconds >= VALID_DWELL_SECONDS,
        value=1.0,
    )


def nova_energy(direct_energy: float) -> float:
    """Nova 전파 에너지는 직접 에너지의 제한된 비율만 허용한다."""
    return direct_energy * NOVA_ENERGY_RATIO
