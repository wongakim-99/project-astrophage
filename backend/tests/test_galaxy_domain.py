"""HTTP/DB와 분리된 은하 도메인 규칙 테스트."""

from app.api.galaxy.domain.rules import GALAXY_COLOR_PALETTE, default_galaxy_color


def test_default_galaxy_color_cycles_through_palette() -> None:
    assert default_galaxy_color(existing_count=0) == GALAXY_COLOR_PALETTE[0]
    assert default_galaxy_color(existing_count=len(GALAXY_COLOR_PALETTE)) == (
        GALAXY_COLOR_PALETTE[0]
    )
