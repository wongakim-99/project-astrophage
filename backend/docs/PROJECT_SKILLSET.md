# Backend — 기술스택 명세

> FastAPI + PostgreSQL(pgvector) 기반. 임베딩 파이프라인, 벡터 유사도 검색, JWT 인증을 단일 Python 생태계로 구성한다.

---

## 핵심 스택

| 역할 | 기술 | 선택 이유 |
|------|------|----------|
| 웹 프레임워크 | **FastAPI** | 비동기 지원, Pydantic 내장, OpenAPI 자동 생성 |
| DB | **PostgreSQL (Railway)** | pgvector 확장으로 벡터 검색, 무료 티어 |
| 벡터 검색 | **pgvector** | 코사인 유사도 쿼리를 SQL 레벨에서 처리 |
| ORM | **SQLAlchemy 2.x (async)** | asyncpg 드라이버와 조합, FastAPI async 호환 |
| DB 마이그레이션 | **Alembic** | SQLAlchemy 공식 마이그레이션 툴 |
| 임베딩 | **OpenAI Python SDK (async)** | `text-embedding-3-small` (1536차원, 저렴) |
| 좌표 배치 | **numpy 휴리스틱** | 코사인 유사도 가중 중심 + jitter (UMAP 미사용) |
| 수치 계산 | **numpy** | 코사인 유사도 계산, 벡터 연산 |
| 인증 | **python-jose[cryptography]** | JWT Access/Refresh Token 생성·검증 |
| 패스워드 해싱 | **bcrypt (직접 호출)** | passlib 없이 `bcrypt.hashpw`/`checkpw` 사용 |
| 데이터 검증 | **Pydantic v2** | FastAPI 내장, request/response 스키마 |
| ASGI 서버 | **Uvicorn** | FastAPI 공식 권장 서버 |
| 환경변수 | **python-dotenv** | `.env` 파일 로드 |

---

## 우주 모델 — 하이브리드 (개인 우주 + 이중 공개 토글)

- 각 유저는 본인만의 갤럭시/스타 소유 (격리된 개인 우주)
- 공개는 **유저 레벨 + 항성 레벨 이중 토글**:
  - `users.is_universe_public` (BOOLEAN, default false) — 유저 우주 마스터 스위치.
  - `stars.is_public` (BOOLEAN, default false) — 항성 단위 토글.
  - 두 컬럼이 **모두 true**여야 공개 URL과 `/explore`에 노출된다.
- 공개 스타 URL: `/:username/stars/:slug` (비로그인 접근 가능)
- 슬러그는 **유저 내 유일** (user_id + slug 복합 유니크 제약)
- 비공개·미존재 모두 **403으로 통합 응답** (enumeration 방어).

---

## 인증 설계

```
Access Token
  - 만료: settings.access_token_expire_minutes (기본 30분)
  - 저장: 프론트엔드 메모리(Zustand) — localStorage 금지(XSS 취약)
  - 헤더: Authorization: Bearer <token>

Refresh Token
  - 만료: settings.refresh_token_expire_days (기본 30일)
  - 저장: httpOnly 쿠키 (samesite=lax, 운영 환경에서 secure=true)
  - 엔드포인트: POST /auth/refresh — 쿠키에서 직접 읽음
  - Rotation: MVP 미구현. /auth/refresh는 access만 새로 발급하고 refresh 쿠키는 그대로 둔다.
    (보안 강화 시 별도 작업으로 rotation 도입 예정.)

비밀번호 해싱
  - bcrypt 직접 사용 (passlib 미사용)
  - rounds: development=8, production=12
```

---

## 임베딩 파이프라인

```
항성 생성 요청
  → OpenAI text-embedding-3-small API 호출 (1536차원, async)
  → pgvector 컬럼에 저장 (Vector(1536))
  → 같은 은하 내 기존 항성과 코사인 유사도 계산 (numpy)
  → place_new_star(...)로 (pos_x, pos_y) 1회 산정
  → DB 저장 후 commit

항성 수정 요청
  → title/content가 바뀌었을 때만 임베딩 재호출
  → embedding 컬럼은 갱신, pos_x/pos_y는 절대 갱신하지 않음
```

### 좌표 배치 전략 (`umap_service.place_new_star`)
- **UMAP/차원축소 사용하지 않음**. (`umap-learn` 의존성은 정리 예정.)
- 기존 항성 좌표는 어떤 경우에도 다시 쓰지 않는다 — 사용자가 익힌 우주 지도를 보존하기 위한 핵심 규칙.
- 신규 항성 한 개에 대해서만 좌표를 산정:
  - 0개 이웃 → `(0, 0)`.
  - 1개 이웃 → `(neighbor.x + 12, neighbor.y)`.
  - 2개 이상 → 코사인 유사도 상위 **k=3** 항성의 가중 중심점.
- 모든 케이스에 ±6.0 단위 jitter (`_JITTER_SCALE = 6.0`)를 더해 의미적으로 가까운 이웃과 좌표가 겹쳐 클릭 불가능해지는 문제를 방지.
- 웜홀 자동 생성 로직은 MVP에 포함되지 않는다 (모델만 존재).

---

## 항성 생애주기 에너지 점수

```
에너지 점수 = sum(view_events.energy_value where is_valid = true)
  단, 최근 30일 이내 이벤트만 집계 (슬라이딩 윈도우)

이벤트별 energy_value:
  유효 조회 (체류 ≥ 30s)  : 1.0   (is_valid=true,  is_edit=false)
  편집 (체류 무관)        : 2.0   (is_valid=true,  is_edit=true)
  Nova 전파 (1-hop)        : 0.25 또는 0.5
                            (is_valid=true,  is_edit=false, 별도 row)

상태 기준 (lifecycle.py 상수):
  주계열성   (MAIN_SEQUENCE) : energy_score ≥ 3.0    (ENERGY_THRESHOLD_ACTIVE)
  황색 왜성  (YELLOW_DWARF)  : 그 외 활성             (energy_score < 3.0)
  적색 거성  (RED_GIANT)     : 마지막 유효 조회 후 60일+ (DAYS_RED_GIANT_START)
  백색 왜성  (WHITE_DWARF)   : 마지막 유효 조회 후 90일+ (DAYS_WHITE_DWARF_START)
  암흑 물질  (DARK_MATTER)   : 마지막 유효 조회 후 180일+ (DAYS_DARK_MATTER_START)

비활성 기간 분기가 활성 분기보다 우선한다 (오래된 항성은 점수 높아도 적색거성).
```

### Nova 에너지 전파
- 유효 조회/편집 이벤트가 `is_valid = true`일 때 → 같은 은하 내 코사인 유사도 상위 **k=5** 항성에 전파.
- 전파량: `base_energy × NOVA_ENERGY_RATIO` (0.25 고정).
  - 조회 기반 전파: `1.0 × 0.25 = 0.25`
  - 편집 기반 전파: `2.0 × 0.25 = 0.5`
- 대상 항성에 새 `view_events` row를 만든다 (`is_valid=true, is_edit=false, duration_seconds=0`).
- 전파는 1-hop 한정. 2-hop 전파 금지.
- 웜홀은 사용하지 않는다 — Nova 대상은 코사인 유사도(`pgvector <=>`) 단독.

---

## 디렉토리 구조 (현재)

```
backend/
├── app/
│   ├── main.py              # FastAPI 앱 진입점, CORS, 라우터 등록
│   ├── core/
│   │   ├── config.py        # pydantic-settings 기반 환경변수
│   │   ├── security.py      # JWT 생성/검증, bcrypt 직접 호출
│   │   ├── database.py      # SQLAlchemy async 세션
│   │   └── dependencies.py  # CurrentUser 등 FastAPI Depends
│   ├── models/              # SQLAlchemy ORM 모델
│   │   ├── base.py
│   │   ├── user.py          # username, email, is_universe_public
│   │   ├── galaxy.py
│   │   ├── star.py          # embedding(Vector), pos_x, pos_y, is_public
│   │   ├── view_event.py    # is_valid, is_edit, energy_value
│   │   └── wormhole.py      # Phase 2 — 스키마만
│   ├── schemas/             # Pydantic v2 request/response
│   │   ├── auth.py / common.py / galaxy.py / star.py
│   ├── repositories/        # SQLAlchemy 쿼리 전담 (3계층 중 데이터 계층)
│   │   ├── user_repo.py
│   │   ├── galaxy_repo.py
│   │   ├── star_repo.py     # find_similar_in_galaxy, list_public 등
│   │   └── view_event_repo.py
│   ├── routers/             # HTTP 진입점, 비즈니스 로직 금지
│   │   ├── auth.py
│   │   ├── stars.py
│   │   ├── galaxies.py
│   │   └── explore.py       # /explore + /:username/stars/:slug
│   └── services/            # 비즈니스 로직 계층
│       ├── auth_service.py
│       ├── galaxy_service.py
│       ├── star_service.py  # NOVA_K, _propagate_nova
│       ├── embedding.py     # OpenAI 임베딩 호출
│       ├── umap_service.py  # 파일명 유지(legacy), 실제로는 휴리스틱 배치
│       └── lifecycle.py     # 에너지 점수, 상태 판정
├── alembic/                 # DB 마이그레이션
├── tests/                   # pytest (auth, galaxies, stars)
├── .env / .env.example
└── requirements.txt
```

> `umap_service.py` 파일명은 초기 설계의 흔적으로 유지 중. 내용은 UMAP을 쓰지 않는 휴리스틱이며, 향후 `placement.py` 등으로 리네이밍 검토 가능.

---

## PostgreSQL 스키마 (현재)

```sql
-- 유저
users (id UUID PK, username VARCHAR(50) UNIQUE, email VARCHAR(255) UNIQUE,
       password_hash VARCHAR(255),
       is_universe_public BOOLEAN DEFAULT false,  -- 유저 우주 공개 마스터 스위치
       created_at TIMESTAMP, updated_at TIMESTAMP)

-- 은하 (유저별 격리)
galaxies (id UUID PK, user_id UUID FK→users, name VARCHAR,
          slug VARCHAR, color VARCHAR,  -- hex, 생성 시 팔레트 자동 배정
          created_at TIMESTAMP, updated_at TIMESTAMP)

-- 항성
stars (id UUID PK, user_id UUID FK→users, galaxy_id UUID FK→galaxies,
       title VARCHAR(200), slug VARCHAR(200), content TEXT,
       embedding VECTOR(1536),    -- pgvector
       pos_x FLOAT, pos_y FLOAT,  -- 휴리스틱 배치 후 고정
       is_public BOOLEAN DEFAULT false,
       created_at TIMESTAMP, updated_at TIMESTAMP,
       UNIQUE(user_id, slug))     -- uq_star_user_slug: 유저 내 슬러그 유일

-- 조회/편집/Nova 이벤트 (에너지 점수 원천)
view_events (id UUID PK, star_id UUID FK→stars, user_id UUID FK→users,
             started_at TIMESTAMP DEFAULT now(),
             duration_seconds INT DEFAULT 0,
             is_valid BOOLEAN DEFAULT false,    -- duration ≥ 30s OR is_edit OR Nova 전파
             is_edit BOOLEAN DEFAULT false,
             energy_value FLOAT DEFAULT 1.0)    -- 1.0 / 2.0 / 0.25 / 0.5

-- 웜홀 (Phase 2, 스키마만 준비, 자동 생성/조회 로직 없음)
wormholes (id UUID PK, star_a_id UUID FK→stars, star_b_id UUID FK→stars,
           similarity FLOAT, created_at TIMESTAMP,
           UNIQUE(star_a_id, star_b_id))
```

---

## 주요 API 엔드포인트 (현재 구현 기준)

| Method | Path | 인증 | 설명 |
|--------|------|------|------|
| POST | `/auth/register` | 없음 | 회원가입. access token 본문 + refresh token httpOnly 쿠키. 충돌 시 409 |
| POST | `/auth/login` | 없음 | 로그인. 동일한 토큰 발급 패턴. 실패 시 401 |
| POST | `/auth/refresh` | 쿠키 | 쿠키의 refresh token 검증, **access만 새로 발급** (rotation 없음) |
| POST | `/auth/logout` | 없음 | Refresh Token 쿠키 삭제 |
| GET | `/auth/me` | 필요 | 현재 사용자 프로필 + `is_universe_public` |
| PATCH | `/auth/me/settings` | 필요 | 유저 우주 공개 토글 (`is_universe_public`) |
| GET | `/galaxies` | 필요 | 본인 은하 목록 |
| POST | `/galaxies` | 필요 | 은하 생성. 슬러그 충돌 시 409 |
| PATCH | `/galaxies/:id` | 필요 | 은하 이름/색상 수정 |
| DELETE | `/galaxies/:id` | 필요 | 은하 삭제 |
| GET | `/stars/galaxy/:galaxy_id` | 필요 | 은하 내 본인 항성 + 좌표 + 생애주기 상태 |
| POST | `/stars/preview-similar` | 필요 | 저장 전 임베딩 호출해 유사 항성 미리보기 (의도적 GET 외 임베딩 호출) |
| POST | `/stars` | 필요 | 항성 생성 (임베딩 계산 + 좌표 배치). 슬러그 충돌 시 409 |
| PUT | `/stars/:id` | 필요 | 항성 수정. title/content 변경 시에만 임베딩 재계산, 좌표는 고정 |
| DELETE | `/stars/:id` | 필요 | 항성 삭제 |
| POST | `/stars/:id/view` | 필요 | 체류/편집 이벤트 기록 + 유효 시 Nova 전파 |
| PATCH | `/stars/:id/visibility` | 필요 | 항성 단위 공개 토글 (`is_public`) |
| GET | `/explore` | 없음 | 공개 스타 카드 피드 (`updated_at desc`, limit 1~100) |
| GET | `/:username/stars/:slug` | 없음 | 공개 스타 페이지. 미존재·비공개 모두 403 |
| GET | `/health` | 없음 | 헬스체크 |
