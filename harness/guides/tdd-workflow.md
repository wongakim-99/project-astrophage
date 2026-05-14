# TDD 워크플로우 가이드

이 프로젝트의 백엔드 개발은 반드시 아래 순서를 따른다.
**구현 파일(`app/`)을 건드리기 전에 테스트를 먼저 작성한다.**

---

## 순서

```
1. SPEC     요구사항 확인 (PROJECT_DOCS.md 또는 대화)
2. TEST     테스트 파일 작성 → pytest 실행 → RED 확인
3. IMPL     최소 구현 → pytest 실행 → GREEN 확인
4. REFACTOR 리팩터링 → pytest 재실행 → GREEN 유지
5. SENSOR   ruff + mypy + pytest 전체 통과 확인
```

---

## 새 API 엔드포인트 체크리스트

### Step 1 — 테스트 파일 먼저

```
tests/test_<기능명>.py 생성
```

포함해야 할 항목:
- [ ] Happy path (정상 케이스)
- [ ] 인증 없음 → 401
- [ ] 권한 없음 (타인 리소스) → 403
- [ ] 존재하지 않는 리소스 → 404
- [ ] 잘못된 입력값 → 422
- [ ] 공개/비공개 이중 플래그 케이스 (해당 시)
- [ ] 슬러그 중복 → 409 (해당 시)

### Step 2 — conftest.py 픽스처 활용

```python
# 인증 필요 → auth_client 사용
async def test_something(auth_client):
    client, user = auth_client
    ...

# 인증 불필요 → client 사용
async def test_public(client):
    ...
```

### Step 3 — 임베딩 mock 필수 확인

테스트 파일에 `embed_text` 실제 호출이 없는지 확인한다.
`conftest.py`의 `client` / `auth_client` 픽스처가 이미 mock을 주입하므로
**픽스처를 우회하면 안 된다.**

---

## 레이어 구현 순서

테스트가 RED 상태일 때 구현은 아래 순서로:

```
1. app/models/       — 모델 변경이 필요한 경우만
2. app/repositories/ — DB 쿼리
3. app/services/     — 비즈니스 로직
4. app/routers/      — HTTP 진입점 (마지막)
```

라우터를 먼저 만들고 서비스를 채우는 방식 금지.

---

## 실패 시 처리

```
pytest 3회 연속 실패 → 사용자에게 판단 위임
```

억측으로 계속 수정하지 말 것. 실패 로그 전체를 사용자에게 보여주고 방향을 확인한다.
