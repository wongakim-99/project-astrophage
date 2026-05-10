# CLAUDE.md — Project Astrophage

AI 에이전트가 이 프로젝트에서 작업하기 전에 반드시 읽어야 하는 문서.
기획 상세는 `PROJECT_DOCS.md`, 스택 상세는 `backend/docs/PROJECT_SKILLSET.md` / `frontend/docs/PROJECT_SKILLSET.md` 참조.

---

## 1. 프로젝트 철학

"인간의 뉴런 구조 == 우주 구조"라는 철학 하에, 개인 지식을 우주 메타포로 시각화하는 블로그.
잊혀진 지식은 암흑 물질이 되고, 복습할수록 항성이 밝아진다.

**절대 잊지 말 것**: 모든 기능 결정의 기준은 이 철학과 탐색 경험(UX)이다.
기술적으로 가능해도 이 철학을 해치면 구현하지 않는다.

---

## 2. 기술 스택

| 영역 | 기술 |
|------|------|
| 백엔드 | FastAPI (Python) |
| DB | PostgreSQL + pgvector (Railway) |
| ORM | SQLAlchemy 2.x async + asyncpg |
| 마이그레이션 | Alembic |
| 임베딩 | OpenAI `text-embedding-3-small` (1536차원) |
| 좌표 배치 | 코사인 유사도 가중 중심 + 랜덤 jitter (UMAP 미사용) |
| 인증 | python-jose (JWT) + bcrypt (직접 호출) |
| 프론트엔드 | React 18.3 + TypeScript + Vite |
| 3D 렌더링 | @react-three/fiber + @react-three/drei + @react-three/postprocessing |
| 상태 관리 | Zustand |
| 라우팅 | React Router v7 |
| 스타일 | TailwindCSS v4 |
| 마크다운 렌더링 | react-markdown + remark-gfm |
| 마크다운 에디터 | @tiptap/react + @tiptap/starter-kit (+ placeholder extension) |
| 검색 | cmdk (Cmd+K 커맨드 팔레트) |
| API 통신 | TanStack Query v5 + axios |

---

## 3. 아키텍처 규칙

### 레이어드 아키텍처 (헥사고날 DDD 아님)
개인 프로젝트 규모에 맞게 심플한 3계층을 유지한다.

```
Router (HTTP 진입점)
  └── Service (비즈니스 로직)
        └── Repository (DB 접근)
```

- **Router**: 요청 파싱, 응답 직렬화만. 비즈니스 로직 작성 금지.
- **Service**: 모든 비즈니스 로직. DB와 직접 통신 금지, 반드시 Repository 경유.
- **Repository**: SQLAlchemy 쿼리만. 비즈니스 판단 금지.

### 임베딩 호출 규칙 ★ 중요
- 임베딩 계산은 **항성 생성 / 수정 시에만** 호출한다.
- **조회(GET) 시 OpenAI API 절대 호출 금지.**
- 임베딩 벡터는 DB에 저장 후 재사용한다. 동일 항성 재계산 불가.

### 좌표 고정 규칙 ★ 중요
- 항성의 `pos_x`, `pos_y`는 **생성 시 1회 계산 후 고정**한다.
- 신규 항성 추가 시 기존 항성 좌표를 절대 덮어쓰지 않는다.
- 신규 항성 배치 알고리즘 (`umap_service.place_new_star`):
  - 기존 항성 0개: 원점 `(0, 0)`.
  - 기존 항성 1개: 단일 항성 기준 `(+12, 0)`에 jitter 적용.
  - 기존 항성 2개 이상: 코사인 유사도 상위 **k=3** 항성의 가중 중심점.
  - 모든 케이스에 ±6.0 단위 랜덤 jitter를 더해 의미적으로 겹치는 항성도 클릭 가능하게 한다.
- UMAP 등 차원 축소는 사용하지 않는다 (의존성도 비활성). 좌표는 임베딩 공간이 아니라 "유사 이웃 근처에 끼워 넣기" 휴리스틱이다.
- 수동 재계산 기능은 현재 미제공. 추후 도입 시에도 별도 명시적 엔드포인트로만 노출한다.

### 공개/비공개 규칙 ★ 중요
공개는 **유저 레벨 + 항성 레벨 이중 토글**이다. 둘 다 true여야 외부에 노출된다.

- `User.is_universe_public` (기본 false): 유저 단위 마스터 스위치. `/auth/me/settings`에서 토글.
- `Star.is_public` (기본 false): 항성 단위 토글. `/stars/:id/visibility`에서 토글.
- 공개 엔드포인트(`/:username/stars/:slug`, `/explore`)는 두 플래그 모두 true인 항성만 반환한다.
- 명시적인 사용자 액션(토글) 없이 공개 처리 절대 금지.
- 공개 슬러그 미존재·비공개·유저 우주 비공개 — **모든 케이스를 통합 403으로 반환**한다 (enumeration 방어). 404로 분기하지 않는다.

### 에너지 점수 계산
- 유효 조회: 30초 이상 체류 = `energy_value = 1.0`
- 편집(저장) 이벤트: `energy_value = 2.0`. **편집은 체류 시간과 무관하게 항상 `is_valid = true`**로 기록한다.
- 점수는 `view_events.is_valid = true`인 이벤트의 `energy_value` 합으로 계산한다 (단순 카운트 아님).
- 집계 범위: 최근 30일 슬라이딩 윈도우.
- 계산은 `lifecycle.py` 서비스 레이어에서만. DB 쿼리에 비즈니스 로직 혼입 금지.
- MVP: GET 요청 시 실시간 계산. 나중에 배치 job으로 전환 가능하도록 서비스 레이어로 분리 유지.

### Nova 에너지 전파
- 유효 조회/편집 이벤트 발생 시 동일 은하 내 코사인 유사도 상위 **k=5** 항성에 전파.
- 전파량: 원본 이벤트의 `energy_value × 0.25` (`NOVA_ENERGY_RATIO = 0.25` 고정).
- 전파 결과는 대상 항성의 `view_events`에 `energy_value = 0.25 또는 0.5`, `is_valid = true`, `is_edit = false`로 기록된다.
- 전파는 1-hop만. 전파의 전파(2-hop) 구현 금지.
- pgvector `<=>` 연산자로 동일 은하(`galaxy_id`) 내 상위 k 항성 쿼리.
- 웜홀은 MVP에서 사용하지 않는다 — Nova 대상 선정은 **코사인 유사도 단독**.

---

## 4. AI 에이전트 금지 사항

아래 행동은 어떤 상황에서도 하지 않는다.

| 금지 행동 | 이유 |
|----------|------|
| 테스트 중 OpenAI API 실제 호출 | 비용 발생. 반드시 mock 사용 |
| 기존 항성의 `pos_x`, `pos_y` 덮어쓰기 | 탐색 경험 파괴 |
| `is_public` + `is_universe_public` 둘 중 하나라도 미확인 | 비공개 데이터 노출 |
| 기존 항성 좌표를 일괄로 다시 계산 (UMAP 등) | 사용자가 익힌 우주 지도 파괴 |
| GET 엔드포인트에서 임베딩 API 호출 (단, `POST /stars/preview-similar`는 의도적 예외) | 비용 + 응답 지연 |
| 슬러그 중복 시 자동 suffix 부여 | 명시적 결정: 유저가 직접 수정, 백엔드는 409 Conflict로 알림 |
| 웜홀 자동 생성/조회/Nova 대상 사용 | Phase 2 범위. 모델은 스키마만 존재 |
| 행성(Planet) 계층 구현 | Phase 3+ 범위 |

---

## 5. Sensors (검증 기준)

작업 완료 전 반드시 통과해야 하는 자동 검증.

### 백엔드
```bash
# 타입 검사
mypy app/

# 테스트 (실제 DB, 실제 OpenAI API 호출 없이)
pytest tests/ -v

# 린트
ruff check app/
```

### 프론트엔드
```bash
# 타입 검사
tsc --noEmit

# 린트
eslint src/

# 빌드 검증
vite build
```

### 테스트 작성 규칙
- OpenAI 임베딩 호출은 **반드시 mock** 처리. `app.services.embedding.embed_text`를 직접 패치한다.
  ```python
  # 예시
  with patch("app.services.embedding.embed_text", new=AsyncMock(return_value=[0.1] * 1536)):
      ...
  ```
- DB 테스트는 테스트 전용 PostgreSQL (인메모리 SQLite 금지 — pgvector 미지원).
- 각 테스트는 독립적 트랜잭션 롤백으로 격리.
- 프론트엔드는 현재 단위 테스트 러너(Vitest 등)를 도입하지 않았다. 검증은 `tsc --noEmit` + `eslint` + `vite build` + 수동 브라우저 확인이다.

---

## 6. 개발 루프

모든 기능 구현은 아래 순서를 지킨다.

```
1. 요구사항 정의
   └── PROJECT_DOCS.md 또는 대화에서 기능 명세 확인

2. 테스트 작성 (TDD)
   └── 구현 전 실패하는 테스트 먼저 작성
   └── OpenAI / UMAP은 mock으로 대체

3. 구현
   └── 레이어드 아키텍처 준수
   └── 금지 사항 체크리스트 확인

4. Sensors 통과
   └── pytest / tsc / ruff / eslint 모두 통과 확인

5. 커밋
   └── 커밋은 사용자가 직접 한다. AI 에이전트가 git commit 실행 금지.
   └── 컨벤션 참고용: feat/fix/refactor/test/chore
```

---

## 7. Python 작성 규칙

- **Python 3.12 사용. `__init__.py` 생성 금지.**
  Python 3.3+ implicit namespace packages로 불필요. 만들지 않아도 모듈 임포트 정상 동작.
- 타입 힌트 전면 사용 (mypy strict 기준).
- async/await 일관 사용 (FastAPI + SQLAlchemy async 환경).

---

## 8. 주요 결정 사항 빠른 참조

| 항목 | 결정 |
|------|------|
| 우주 모델 | 하이브리드: 개인 우주 기본, 유저 토글 + 항성 토글의 이중 publish |
| URL | `/:username/stars/:slug` (유저 내 슬러그 유일) |
| 비로그인 랜딩 | `/universes` — 공개 피드 + 히어로 섹션 |
| 공개 우주 | `/explore` — 카드 피드, `Star.updated_at desc` 정렬 |
| 항성 생성/편집 | 모달이 아닌 풀페이지 (`/galaxy/:id/new`, `/galaxy/:id/edit/:starId`) |
| 검색 | `Cmd+K` 커맨드 팔레트 → 항성 fly-in (Sidebar는 별도 도구바 용도) |
| 좌표계 | 2D (z=0), 가중 중심 + jitter로 1회 배치 후 고정 (UMAP 미사용) |
| 에너지 계산 | MVP 실시간, 추후 배치 job 전환 |
| 은하 경계 | 반투명 성운(nebula) 안개 효과 |
| 은하 색상 | 생성 시 팔레트 자동 배정, 이후 변경 가능 |
| 슬러그 | 제목에서 자동 제안, 유저 직접 수정 가능, 충돌 시 409 Conflict |
| Refresh token | httpOnly 쿠키, MVP는 rotation 미구현 (재발급 시 access만 갱신) |
| 모바일 | 우주 탐색 뷰 미지원, 블로그 포스트만 반응형 |
| 행성 | 메타포만, 미구현 |
| 웜홀 | Phase 2 (모델만 존재, 자동 생성/Nova 사용 X) |
