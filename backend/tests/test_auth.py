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
    # Refresh token set as httpOnly cookie
    assert "refresh_token" in response.cookies


async def test_login_wrong_password(client: AsyncClient) -> None:
    await client.post("/auth/register", json={
        "username": "pwtest", "email": "pw@cosmos.dev", "password": "correct1"
    })
    response = await client.post("/auth/login", json={
        "email": "pw@cosmos.dev", "password": "wrongpassword"
    })
    assert response.status_code == 401


async def test_logout(client: AsyncClient) -> None:
    response = await client.post("/auth/logout")
    assert response.status_code == 200
    assert response.json()["message"] == "Logged out"


async def test_health(client: AsyncClient) -> None:
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
