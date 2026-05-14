"""
새 API 엔드포인트 테스트 템플릿.

사용법:
  1. 이 파일을 backend/tests/test_<기능명>.py 로 복사
  2. TODO 항목을 실제 값으로 채운다
  3. pytest 실행 → RED 확인
  4. 구현 후 GREEN 확인

픽스처는 conftest.py에서 자동 주입된다.
embed_text mock도 conftest.py가 처리하므로 별도 patch 불필요.
"""

import pytest
from httpx import AsyncClient

from app.models.user import User

# TODO: 테스트 대상 엔드포인트
# ENDPOINT = "/stars"
# METHOD   = "POST"


# ── Happy Path ────────────────────────────────────────────

@pytest.mark.asyncio
async def test_<기능명>_success(auth_client: tuple[AsyncClient, User]) -> None:
    """정상 케이스: 올바른 요청 → 200/201."""
    client, user = auth_client

    # TODO: 요청 데이터
    payload = {}

    resp = await client.post("/TODO", json=payload)
    assert resp.status_code == 201

    data = resp.json()
    # TODO: 응답 필드 검증
    # assert data["id"] is not None


# ── 인증 ─────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_<기능명>_requires_auth(client: AsyncClient) -> None:
    """인증 없음 → 401."""
    resp = await client.post("/TODO", json={})
    assert resp.status_code == 401


# ── 권한 ─────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_<기능명>_forbidden_for_other_user(auth_client: tuple[AsyncClient, User]) -> None:
    """타인 리소스 접근 → 403."""
    client, user = auth_client

    # TODO: 다른 유저 소유 리소스 ID 삽입
    other_resource_id = "00000000-0000-0000-0000-000000000000"

    resp = await client.get(f"/TODO/{other_resource_id}")
    assert resp.status_code == 403


# ── 존재하지 않는 리소스 ──────────────────────────────────

@pytest.mark.asyncio
async def test_<기능명>_not_found(auth_client: tuple[AsyncClient, User]) -> None:
    """없는 리소스 → 404."""
    client, _ = auth_client

    resp = await client.get("/TODO/nonexistent-id")
    assert resp.status_code == 404


# ── 잘못된 입력 ───────────────────────────────────────────

@pytest.mark.asyncio
async def test_<기능명>_invalid_payload(auth_client: tuple[AsyncClient, User]) -> None:
    """필수 필드 누락 → 422."""
    client, _ = auth_client

    resp = await client.post("/TODO", json={})  # 빈 payload
    assert resp.status_code == 422


# ── 도메인 규칙 엣지케이스 ───────────────────────────────
# 아래는 이 프로젝트 특유의 케이스. 해당하는 것만 활성화.

# @pytest.mark.asyncio
# async def test_<기능명>_slug_conflict(auth_client):
#     """슬러그 중복 → 409 Conflict."""
#     client, user = auth_client
#     # 동일 슬러그로 두 번 생성
#     payload = {"slug": "duplicate-slug", ...}
#     await client.post("/TODO", json=payload)
#     resp = await client.post("/TODO", json=payload)
#     assert resp.status_code == 409

# @pytest.mark.asyncio
# async def test_<기능명>_private_universe_hidden(client):
#     """유저 우주 비공개 → 공개 엔드포인트에서 403."""
#     # User.is_universe_public = False 상태에서 공개 접근
#     resp = await client.get("/username/stars/slug")
#     assert resp.status_code == 403

# @pytest.mark.asyncio
# async def test_<기능명>_star_private_hidden(client):
#     """항성 비공개 → 공개 엔드포인트에서 403."""
#     # Star.is_public = False 상태
#     resp = await client.get("/username/stars/slug")
#     assert resp.status_code == 403
