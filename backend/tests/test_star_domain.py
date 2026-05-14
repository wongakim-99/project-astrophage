"""HTTP/DB와 분리된 항성 도메인 규칙 테스트."""

from app.domain.star.placement import place_new_star
from app.domain.star.rules import (
    NOVA_ENERGY_RATIO,
    VALID_DWELL_SECONDS,
    direct_view_energy,
    embedding_source,
    initial_star_visibility,
    nova_energy,
)


def test_embedding_source_combines_title_and_content() -> None:
    assert embedding_source("Merge Sort", "Divide and conquer") == (
        "Merge Sort\nDivide and conquer"
    )


def test_initial_star_visibility_follows_universe_visibility() -> None:
    assert initial_star_visibility(is_universe_public=True) is True
    assert initial_star_visibility(is_universe_public=False) is False


def test_short_view_has_no_lifecycle_energy() -> None:
    energy = direct_view_energy(duration_seconds=VALID_DWELL_SECONDS - 1, is_edit=False)

    assert energy.is_valid is False
    assert energy.value == 1.0


def test_dwell_view_has_normal_lifecycle_energy() -> None:
    energy = direct_view_energy(duration_seconds=VALID_DWELL_SECONDS, is_edit=False)

    assert energy.is_valid is True
    assert energy.value == 1.0


def test_edit_has_double_lifecycle_energy_without_dwell_time() -> None:
    energy = direct_view_energy(duration_seconds=0, is_edit=True)

    assert energy.is_valid is True
    assert energy.value == 2.0


def test_nova_energy_is_limited_ratio_of_direct_energy() -> None:
    assert nova_energy(2.0) == 2.0 * NOVA_ENERGY_RATIO


def test_new_star_without_existing_neighbors_starts_at_origin() -> None:
    assert place_new_star(existing_stars=[], new_embedding=[0.1, 0.2]) == (0.0, 0.0)
