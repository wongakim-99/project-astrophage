"""헥사고날/DDD 계층 경계 회귀 테스트."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_star_routers_depend_on_application_use_cases() -> None:
    router_sources = [
        PROJECT_ROOT / "app" / "routers" / "stars.py",
        PROJECT_ROOT / "app" / "routers" / "explore.py",
    ]

    for source_path in router_sources:
        source = source_path.read_text(encoding="utf-8")
        assert "app.application.star_use_cases" in source
        assert "app.services.star_service" not in source


def test_star_use_cases_do_not_depend_on_services_layer() -> None:
    source_path = PROJECT_ROOT / "app" / "application" / "star_use_cases.py"
    source = source_path.read_text(encoding="utf-8")

    assert "app.services." not in source
    assert "from app.services" not in source
