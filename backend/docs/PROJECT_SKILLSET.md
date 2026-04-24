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
| 임베딩 | **OpenAI Python SDK** | `text-embedding-3-small` (1536차원, 저렴) |
| 차원 축소 | **umap-learn** | 1536차원 임베딩 → 2D 화면 좌표 변환 |
| 수치 계산 | **numpy + scipy** | 코사인 유사도 계산, 벡터 연산 |
| 인증 | **python-jose[cryptography]** | JWT Access/Refresh Token 생성·검증 |
| 패스워드 해싱 | **passlib[bcrypt]** | 비밀번호 안전한 단방향 해시 |
| 데이터 검증 | **Pydantic v2** | FastAPI 내장, request/response 스키마 |
| ASGI 서버 | **Uvicorn** | FastAPI 공식 권장 서버 |
| 환경변수 | **python-dotenv** | `.env` 파일 로드 |

---

## 우주 모델 — 하이브리드 (개인 우주 + 공개 publish)

- 각 유저는 본인만의 갤럭시/스타 소유 (격리된 개인 우주)
- 스타마다 `is_public` 토글: `true` → 공개 URL 접근 가능 + `/explore` 노출
- 공개 스타 URL: `/:username/stars/:slug` (비로그인 접근 가능)
- 슬러그는 **유저 내 유일** (user_id + slug 복합 유니크 제약)

---

## 인증 설계

```
Access Token
  - 만료: 30분
  - 저장: 프론트엔드 메모리(변수) — localStorage 금지(XSS 취약)
  - 헤더: Authorization: Bearer <token>

Refresh Token
  - 만료: 30일
  - 저장: httpOnly 쿠키 (JS 접근 불가 → XSS 방어)
  - 엔드포인트: POST /auth/refresh
```

---

## 임베딩 파이프라인

```
항성 생성 요청
  → OpenAI text-embedding-3-small API 호출 (1536차원)
  → pgvector 컬럼에 저장
  → 동일 은하 내 기존 항성들과 코사인 유사도 계산 (pgvector <=> 연산자)
  → umap-learn으로 해당 은하 전체 좌표 재계산 (2D x, y)
  → 유사도 임계값(0.88) 초과 시 웜홀 레코드 자동 생성
```

### 좌표 재계산 전략
- 항성이 추가/수정될 때마다 해당 **은하 전체** 좌표를 UMAP으로 재계산
- UMAP은 항성 수 < 1000일 때 수초 내 완료 → 동기 처리 가능
- 항성 수 증가 시 백그라운드 태스크(FastAPI `BackgroundTasks`)로 전환 고려

---

## 항성 생애주기 에너지 점수

```
에너지 점수 = (유효 조회 수 × 1) + (편집 횟수 × 2)
  단, 최근 30일 이내 이벤트만 집계 (슬라이딩 윈도우)

상태 기준 (에너지 점수 기반):
  주계열성 (Active)    : 30일 내 에너지 점수 ≥ 3
  황색 왜성 (Normal)   : 30일 내 에너지 점수 1~2
  적색 거성 (Fading)   : 마지막 유효 조회 후 60~90일 경과
  백색 왜성 (Forgotten): 마지막 유효 조회 후 90일 이상 경과
  암흑 물질 (Lost)     : 마지막 유효 조회 후 180일 이상 경과

유효 조회 조건: 항성 상세 페이지 체류 30초 이상
편집: 마크다운 내용 저장 시
```

### Nova 에너지 전파
- 유효 조회 이벤트 발생 시 → 연결된 항성(웜홀 또는 코사인 유사도 상위 k개)에 에너지 0.2~0.3배 전파
- 전파는 직접 연결된 항성에만 (1-hop), 전파의 전파(2-hop) 없음

---

## 디렉토리 구조 (예정)

```
backend/
├── app/
│   ├── main.py              # FastAPI 앱 진입점
│   ├── core/
│   │   ├── config.py        # 환경변수, 설정값
│   │   ├── security.py      # JWT 생성/검증, bcrypt
│   │   └── database.py      # SQLAlchemy 세션
│   ├── models/              # SQLAlchemy ORM 모델
│   ├── schemas/             # Pydantic 스키마 (request/response)
│   ├── routers/             # FastAPI 라우터
│   │   ├── auth.py
│   │   ├── stars.py
│   │   ├── galaxies.py
│   │   └── wormholes.py
│   └── services/            # 비즈니스 로직
│       ├── embedding.py     # OpenAI 임베딩 호출
│       ├── umap_service.py  # 좌표 계산
│       └── lifecycle.py     # 에너지 점수, 상태 판정
├── alembic/                 # DB 마이그레이션
├── .env
└── requirements.txt
```

---

## PostgreSQL 스키마 (초안)

```sql
-- 유저
users (id UUID PK, username VARCHAR UNIQUE, email VARCHAR UNIQUE,
       password_hash VARCHAR, created_at TIMESTAMP)

-- 은하 (유저별 격리)
galaxies (id UUID PK, user_id UUID FK→users, name VARCHAR,
          slug VARCHAR, color VARCHAR,  -- hex, 생성 시 팔레트 자동 배정
          created_at TIMESTAMP)

-- 항성
stars (id UUID PK, user_id UUID FK→users, galaxy_id UUID FK→galaxies,
       title VARCHAR, slug VARCHAR, content TEXT,
       embedding VECTOR(1536),   -- pgvector
       pos_x FLOAT, pos_y FLOAT, -- UMAP 2D 좌표 (고정)
       is_public BOOLEAN DEFAULT false,
       created_at TIMESTAMP, updated_at TIMESTAMP,
       UNIQUE(user_id, slug))    -- 유저 내 슬러그 유일

-- 조회 이벤트 (에너지 점수 원천)
view_events (id UUID PK, star_id UUID FK→stars, user_id UUID FK→users,
             started_at TIMESTAMP, duration_seconds INT,
             is_valid BOOLEAN,   -- duration >= 30s
             is_edit BOOLEAN DEFAULT false)  -- 편집 이벤트 여부

-- 웜홀 (Phase 2, 스키마만 준비)
wormholes (id UUID PK, star_a_id UUID FK→stars, star_b_id UUID FK→stars,
           similarity FLOAT, created_at TIMESTAMP)
```

---

## 주요 API 엔드포인트

| Method | Path | 인증 | 설명 |
|--------|------|------|------|
| POST | `/auth/register` | 없음 | 회원가입 |
| POST | `/auth/login` | 없음 | 로그인, Token 발급 |
| POST | `/auth/refresh` | 없음 | Refresh Token → Access Token 재발급 |
| POST | `/auth/logout` | 필요 | Refresh Token 쿠키 삭제 |
| GET | `/galaxies` | 필요 | 본인 은하 목록 |
| POST | `/galaxies` | 필요 | 은하 생성 |
| GET | `/galaxies/:id/stars` | 필요 | 은하 내 항성 + 좌표 |
| GET | `/:username/stars/:slug` | 없음 | 공개 스타 페이지 |
| POST | `/stars` | 필요 | 항성 생성 (임베딩 자동 계산, 좌표 배치) |
| PUT | `/stars/:id` | 필요 | 항성 수정 |
| DELETE | `/stars/:id` | 필요 | 항성 삭제 |
| POST | `/stars/:id/view` | 필요 | 유효 조회 이벤트 기록 + Nova 전파 |
| PATCH | `/stars/:id/visibility` | 필요 | is_public 토글 |
| GET | `/explore` | 없음 | 공개 스타 목록 |
