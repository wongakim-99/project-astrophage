# AGENTS.md — Project Astrophage

이 파일은 Claude Code, Codex, Cursor 등 모든 AI 에이전트가 읽는 공용 규칙이다.
CLAUDE.md의 핵심 규칙 중 **에이전트가 자주 위반하는 항목**만 추출했다.

---

## 절대 금지 (시스템이 차단함)

| 행동 | 이유 |
|------|------|
| `git commit` 실행 | 커밋은 사용자가 직접 |
| `git push` 실행 | 원격 반영은 사용자 확인 필요 |
| `pos_x`, `pos_y` UPDATE | 항성 좌표는 생성 시 1회 고정 |
| `alembic downgrade` | 데이터 손실 위험 |
| `rm -rf` | 파괴적 삭제 |

---

## TDD 순서 (반드시 준수)

```
테스트 작성 → RED 확인 → 구현 → GREEN 확인
```

구현 파일(`app/`)을 테스트 없이 먼저 수정하지 않는다.
→ 자세한 순서: `harness/guides/tdd-workflow.md`

---

## 임베딩 규칙

- `embed_text()` 호출 가능 위치: `app/services/` 내 항성 생성/수정 서비스만
- GET 핸들러 (`app/routers/` 내 `@router.get`) 에서 호출 금지
- 테스트에서 실제 OpenAI API 호출 금지 → conftest.py 픽스처가 mock 주입

---

## 공개/비공개 이중 플래그

외부 공개 조건: `User.is_universe_public AND Star.is_public` 둘 다 true
→ 하나라도 false면 403 반환 (404 사용 금지)

---

## 스택 빠른 참조

```
백엔드:  FastAPI + SQLAlchemy 2.x async + PostgreSQL + pgvector
테스트:  pytest-asyncio + httpx AsyncClient + 실제 PostgreSQL (SQLite 금지)
린트:    ruff check app/
타입:    mypy app/
실행:    cd backend && .venv/bin/python -m pytest tests/ -v
```
