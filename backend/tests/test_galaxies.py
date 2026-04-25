"""소유자 범위 CRUD와 기본 색상 배정을 검증하는 은하 API 테스트."""

from httpx import AsyncClient

from app.models.user import User


async def test_create_galaxy(auth_client: tuple[AsyncClient, User]) -> None:
    client, user = auth_client
    response = await client.post("/galaxies", json={
        "name": "Algorithm Galaxy",
        "slug": "algorithm",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Algorithm Galaxy"
    assert data["slug"] == "algorithm"
    assert data["color"].startswith("#")


async def test_create_galaxy_custom_color(auth_client: tuple[AsyncClient, User]) -> None:
    client, _ = auth_client
    response = await client.post("/galaxies", json={
        "name": "Network Galaxy",
        "slug": "network",
        "color": "#FF0000",
    })
    assert response.status_code == 201
    assert response.json()["color"] == "#FF0000"


async def test_create_galaxy_duplicate_slug(auth_client: tuple[AsyncClient, User]) -> None:
    client, _ = auth_client
    await client.post("/galaxies", json={"name": "G1", "slug": "dup-slug"})
    response = await client.post("/galaxies", json={"name": "G2", "slug": "dup-slug"})
    assert response.status_code == 409


async def test_list_galaxies(auth_client: tuple[AsyncClient, User]) -> None:
    client, _ = auth_client
    await client.post("/galaxies", json={"name": "OS Galaxy", "slug": "os"})
    await client.post("/galaxies", json={"name": "DB Galaxy", "slug": "db"})
    response = await client.get("/galaxies")
    assert response.status_code == 200
    slugs = [g["slug"] for g in response.json()]
    assert "os" in slugs
    assert "db" in slugs


async def test_update_galaxy(auth_client: tuple[AsyncClient, User]) -> None:
    client, _ = auth_client
    create_resp = await client.post("/galaxies", json={"name": "Old Name", "slug": "update-test"})
    galaxy_id = create_resp.json()["id"]

    response = await client.patch(f"/galaxies/{galaxy_id}", json={"name": "New Name", "color": "#AABBCC"})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "New Name"
    assert data["color"] == "#AABBCC"


async def test_delete_galaxy(auth_client: tuple[AsyncClient, User]) -> None:
    client, _ = auth_client
    create_resp = await client.post("/galaxies", json={"name": "To Delete", "slug": "del-galaxy"})
    galaxy_id = create_resp.json()["id"]

    response = await client.delete(f"/galaxies/{galaxy_id}")
    assert response.status_code == 200

    list_resp = await client.get("/galaxies")
    ids = [g["id"] for g in list_resp.json()]
    assert galaxy_id not in ids
