"""헥사고날/DDD 계층 경계 회귀 테스트."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_ROOT = PROJECT_ROOT / "app"
API_ROOT = APP_ROOT / "api"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _python_files(path: Path) -> list[Path]:
    if not path.exists():
        return []
    return [p for p in path.rglob("*.py") if "__pycache__" not in p.parts]


def test_feature_contexts_use_pawpong_style_layers() -> None:
    for context in ("auth", "galaxy", "star"):
        context_root = API_ROOT / context
        assert context_root.exists()
        assert (context_root / "application").exists()
        assert (context_root / "dto").exists()
        assert (context_root / "infrastructure").exists()

    assert (API_ROOT / "star" / "domain" / "lifecycle.py").exists()
    assert (API_ROOT / "star" / "domain" / "placement.py").exists()
    assert (API_ROOT / "star" / "domain" / "rules.py").exists()
    assert (API_ROOT / "galaxy" / "domain" / "rules.py").exists()


def test_flat_legacy_layers_have_no_python_modules() -> None:
    for layer in ("adapters", "application", "core", "domain", "models", "ports", "routers", "schemas"):
        assert not _python_files(APP_ROOT / layer)


def test_controllers_depend_on_context_application_use_cases() -> None:
    expectations = {
        API_ROOT / "auth" / "auth_controller.py": "app.api.auth.application.use_cases",
        API_ROOT / "galaxy" / "galaxy_controller.py": "app.api.galaxy.application.use_cases",
        API_ROOT / "star" / "star_controller.py": "app.api.star.application.use_cases",
        API_ROOT / "star" / "explore_controller.py": "app.api.star.application.use_cases",
    }

    for source_path, expected_import in expectations.items():
        source = _read(source_path)
        assert expected_import in source
        assert "app.services." not in source


def test_application_use_cases_depend_on_ports_not_infrastructure() -> None:
    for source_path in API_ROOT.glob("*/application/use_cases.py"):
        source = _read(source_path)
        assert "sqlalchemy" not in source
        assert ".infrastructure." not in source
        assert "app.repositories." not in source
        assert "from app.repositories" not in source


def test_application_use_cases_do_not_depend_on_http_dto() -> None:
    for source_path in API_ROOT.glob("*/application/use_cases.py"):
        source = _read(source_path)
        assert ".dto.auth" not in source
        assert ".dto.galaxy" not in source
        assert ".dto.star" not in source


def test_controllers_do_not_construct_infrastructure_directly() -> None:
    for source_path in API_ROOT.glob("*/*_controller.py"):
        source = _read(source_path)
        assert ".infrastructure." not in source


def test_repositories_are_context_infrastructure_adapters() -> None:
    assert not _python_files(APP_ROOT / "repositories")
    assert (API_ROOT / "auth" / "infrastructure" / "user_repository.py").exists()
    assert (API_ROOT / "galaxy" / "infrastructure" / "galaxy_repository.py").exists()
    assert (API_ROOT / "star" / "infrastructure" / "star_repository.py").exists()
    assert (API_ROOT / "star" / "infrastructure" / "view_event_repository.py").exists()
    assert (APP_ROOT / "common" / "infrastructure" / "persistence" / "unit_of_work.py").exists()
