"""계정 생성, 로그인, 쿠키, 상태 확인을 검증하는 Auth API 회귀 테스트."""

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.user_repo import UserRepository


async def test_register_success(client: AsyncClient, session: AsyncSession) -> None:
    response = await client.post("/auth/register", json={
        "username": "stargazer",
        "email": "stargazer@cosmos.dev",
        "password": "supersecret1",
    })
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

    repo = UserRepository(session)
    user = await repo.get_by_email("stargazer@cosmos.dev")
    assert user is not None
    assert user.username == "stargazer"


async def test_register_duplicate_email(client: AsyncClient) -> None:
    payload = {"username": "nova1", "email": "dup@cosmos.dev", "password": "password1"}
    await client.post("/auth/register", json=payload)

    payload["username"] = "nova2"
    response = await client.post("/auth/register", json=payload)
    assert response.status_code == 409


async def test_register_duplicate_username(client: AsyncClient) -> None:
    await client.post("/auth/register", json={
        "username": "sameuser", "email": "a@cosmos.dev", "password": "password1"
    })
    response = await client.post("/auth/register", json={
        "username": "sameuser", "email": "b@cosmos.dev", "password": "password1"
    })
    assert response.status_code == 409


async def test_login_success(client: AsyncClient) -> None:
    await client.post("/auth/register", json={
        "username": "logintest", "email": "login@cosmos.dev", "password": "mypassword1"
    })
    response = await client.post("/auth/login", json={
        "email": "login@cosmos.dev", "password": "mypassword1"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
    # refresh token은 httpOnly 쿠키로 설정된다.
    assert "refresh_token" in response.cookies


async def test_login_wrong_password(client: AsyncClient) -> None:
    await client.post("/auth/register", json={
        "username": "pwtest", "email": "pw@cosmos.dev", "password": "correct1"
    })
    response = await client.post("/auth/login", json={
        "email": "pw@cosmos.dev", "password": "wrongpassword"
    })
    assert response.status_code == 401


async def test_update_universe_visibility(auth_client) -> None:  # type: ignore[no-untyped-def]
    client, _ = auth_client

    me_response = await client.get("/auth/me")
    assert me_response.status_code == 200
    assert me_response.json()["is_universe_public"] is False

    update_response = await client.patch("/auth/me/settings", json={"is_universe_public": True})
    assert update_response.status_code == 200
    assert update_response.json()["is_universe_public"] is True


async def test_logout(client: AsyncClient) -> None:
    response = await client.post("/auth/logout")
    assert response.status_code == 200
    assert response.json()["message"] == "Logged out"


async def test_health(client: AsyncClient) -> None:
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
