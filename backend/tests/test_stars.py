"""CRUD, 공개 여부, 조회 에너지, 생애주기 규칙을 검증하는 항성 API 테스트."""

from httpx import AsyncClient

from app.models.user import User
from app.services.lifecycle import DAYS_DARK_MATTER_START, compute_lifecycle

# ── 헬퍼 ──────────────────────────────────────────────────────────────────────

async def _make_galaxy(client: AsyncClient, slug: str = "algo") -> str:
    resp = await client.post("/galaxies", json={"name": "Test Galaxy", "slug": slug})
    assert resp.status_code == 201
    return resp.json()["id"]


async def _make_star(client: AsyncClient, galaxy_id: str, slug: str = "merge-sort") -> dict:  # type: ignore[type-arg]
    resp = await client.post("/stars", json={
        "title": "Merge Sort",
        "slug": slug,
        "content": "Divide and conquer sorting algorithm.",
        "galaxy_id": galaxy_id,
    })
    assert resp.status_code == 201
    return resp.json()


# ── 항성 CRUD ─────────────────────────────────────────────────────────────────

async def test_create_star(auth_client: tuple[AsyncClient, User]) -> None:
    client, _ = auth_client
    galaxy_id = await _make_galaxy(client, "algo-create")
    star = await _make_star(client, galaxy_id)

    assert star["title"] == "Merge Sort"
    assert star["slug"] == "merge-sort"
    assert star["is_public"] is False
    assert "pos_x" in star
    assert "pos_y" in star
    assert star["lifecycle_state"] == "yellow_dwarf"


async def test_create_star_duplicate_slug(auth_client: tuple[AsyncClient, User]) -> None:
    client, _ = auth_client
    galaxy_id = await _make_galaxy(client, "algo-dup")
    await _make_star(client, galaxy_id, slug="bubble-sort")

    resp = await client.post("/stars", json={
        "title": "Bubble Sort Again",
        "slug": "bubble-sort",
        "content": "...",
        "galaxy_id": galaxy_id,
    })
    assert resp.status_code == 409


async def test_list_stars_in_galaxy(auth_client: tuple[AsyncClient, User]) -> None:
    client, _ = auth_client
    galaxy_id = await _make_galaxy(client, "algo-list")
    await _make_star(client, galaxy_id, slug="quick-sort")
    await _make_star(client, galaxy_id, slug="heap-sort")

    resp = await client.get(f"/stars/galaxy/{galaxy_id}")
    assert resp.status_code == 200
    slugs = [s["slug"] for s in resp.json()]
    assert "quick-sort" in slugs
    assert "heap-sort" in slugs


async def test_update_star(auth_client: tuple[AsyncClient, User]) -> None:
    client, _ = auth_client
    galaxy_id = await _make_galaxy(client, "algo-upd")
    star = await _make_star(client, galaxy_id, slug="insertion-sort")

    resp = await client.put(f"/stars/{star['id']}", json={"title": "Insertion Sort (Updated)"})
    assert resp.status_code == 200
    assert resp.json()["title"] == "Insertion Sort (Updated)"


async def test_delete_star(auth_client: tuple[AsyncClient, User]) -> None:
    client, _ = auth_client
    galaxy_id = await _make_galaxy(client, "algo-del")
    star = await _make_star(client, galaxy_id, slug="selection-sort")

    resp = await client.delete(f"/stars/{star['id']}")
    assert resp.status_code == 200

    list_resp = await client.get(f"/stars/galaxy/{galaxy_id}")
    ids = [s["id"] for s in list_resp.json()]
    assert star["id"] not in ids


# ── 공개 여부 ─────────────────────────────────────────────────────────────────

async def test_visibility_toggle(auth_client: tuple[AsyncClient, User]) -> None:
    client, user = auth_client
    galaxy_id = await _make_galaxy(client, "algo-vis")
    star = await _make_star(client, galaxy_id, slug="radix-sort")
    assert star["is_public"] is False

    resp = await client.patch(f"/stars/{star['id']}/visibility", json={"is_public": True})
    assert resp.status_code == 200
    assert resp.json()["is_public"] is True

    # 공개 전환 후에는 공개 페이지로 접근할 수 있어야 한다.
    pub_resp = await client.get(f"/{user.username}/stars/radix-sort")
    assert pub_resp.status_code == 200
    assert pub_resp.json()["title"] == "Merge Sort" or pub_resp.json()["title"] == "Radix Sort"


async def test_private_star_returns_403(auth_client: tuple[AsyncClient, User]) -> None:
    client, user = auth_client
    galaxy_id = await _make_galaxy(client, "algo-priv")
    await _make_star(client, galaxy_id, slug="private-star")

    resp = await client.get(f"/{user.username}/stars/private-star")
    assert resp.status_code == 403


# ── 조회 이벤트와 생애주기 ───────────────────────────────────────────────────

async def test_record_view_valid(auth_client: tuple[AsyncClient, User]) -> None:
    client, _ = auth_client
    galaxy_id = await _make_galaxy(client, "algo-view")
    star = await _make_star(client, galaxy_id, slug="counting-sort")

    resp = await client.post(f"/stars/{star['id']}/view", json={"duration_seconds": 35})
    assert resp.status_code == 200
    data = resp.json()
    assert data["energy_score"] >= 1.0


async def test_record_view_invalid_too_short(auth_client: tuple[AsyncClient, User]) -> None:
    client, _ = auth_client
    galaxy_id = await _make_galaxy(client, "algo-view2")
    star = await _make_star(client, galaxy_id, slug="short-view")

    # 10초는 30초 기준보다 짧으므로 유효 조회로 계산되면 안 된다.
    resp = await client.post(f"/stars/{star['id']}/view", json={"duration_seconds": 10})
    assert resp.status_code == 200
    assert resp.json()["energy_score"] == 0.0


async def test_edit_event_gives_double_energy(auth_client: tuple[AsyncClient, User]) -> None:
    client, _ = auth_client
    galaxy_id = await _make_galaxy(client, "algo-edit")
    star = await _make_star(client, galaxy_id, slug="edit-star")

    resp = await client.post(f"/stars/{star['id']}/view", json={"duration_seconds": 0, "is_edit": True})
    assert resp.status_code == 200
    assert resp.json()["energy_score"] == 2.0


# ── 생애주기 단위 테스트 ─────────────────────────────────────────────────────

def test_lifecycle_main_sequence() -> None:
    from datetime import UTC, datetime, timedelta
    from unittest.mock import MagicMock

    events = []
    for _ in range(3):
        e = MagicMock()
        e.is_valid = True
        e.is_edit = False
        e.energy_value = 1.0
        events.append(e)

    last = MagicMock()
    last.started_at = datetime.now(UTC) - timedelta(days=1)

    state, score = compute_lifecycle(events, last)
    assert state.value == "main_sequence"
    assert score == 3.0


def test_lifecycle_dark_matter() -> None:
    from datetime import UTC, datetime, timedelta
    from unittest.mock import MagicMock

    last = MagicMock()
    last.started_at = datetime.now(UTC) - timedelta(days=DAYS_DARK_MATTER_START + 1)

    state, score = compute_lifecycle([], last)
    assert state.value == "dark_matter"


def test_lifecycle_no_events_is_yellow_dwarf() -> None:
    state, score = compute_lifecycle([], None)
    assert state.value == "yellow_dwarf"
    assert score == 0.0
