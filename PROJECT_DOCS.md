# Project Astrophage — 기획 검토 문서

> README 초안을 기반으로 기획의 타당성 검토, 모호한 지점 정리, 기술스택 논의 내용을 기록한다.

---

## 1. 기획 타당성 검토

### 잘 정의된 부분

- **우주 메타포 ↔ 지식 구조 매핑** : Galaxy=도메인, Star=개념, Distance=유사도 관계가 명확하고 일관성 있음
- **항성 생애주기** : 실제 천체물리학 기반 5단계(주계열성 → 암흑 물질)가 직관적이며 "잊혀진 지식" 시각화라는 핵심 가치와 직결됨
- **신성(Nova) 에너지 전파** : 연관 개념 복습 시 에너지 소량 전파 (20~30%) — 구현 범위가 명확하고 수치가 구체적임
- **줌 레벨 3단계 렌더링 분리** : LOD + lazy load 전략이 이미 정의되어 있어 성능 설계가 선행된 점이 좋음
- **MVP 범위 분리** : 단일 은하 + CRUD부터 시작하는 접근이 현실적

---

## 2. 결정된 사항

### [A1] 사용자 범위 — 멀티 유저, 인증 필요
- 확장성을 고려하여 회원가입 / 로그인 기능 포함
- JWT 기반 인증: **Access Token (단기)** + **Refresh Token (장기)** 발급
- Access Token: 메모리(변수)에 저장, 15~30분 만료
- Refresh Token: httpOnly 쿠키에 저장, 7~30일 만료 (XSS 공격 방어)
- 외부 공유 블로그 포스트는 비로그인 사용자도 읽기 가능 (공개 엔드포인트)

### [A2] 2D 배치 + Three.js 시각 효과
- 항성은 **z=0 평면**에 배치 (XY 좌표만 사용)
- Three.js(R3F)는 시각 효과 전담 : 파티클, 글로우, 카메라 이동 애니메이션
- 좌표 산정: **UMAP 사용하지 않음**. 신규 항성만 "유사 이웃 가중 중심점 + ±6.0 jitter"로 1회 계산 후 고정. (자세한 알고리즘은 [A16] 참조.)
- 나중에 z축 값만 추가하면 3D 확장 가능하도록 좌표 스키마 설계

### [A3] 행성(Planet) — 메타포만, MVP 미구현
- 행성은 우주 메타포 설명용으로만 존재
- "알고리즘 은하 → 정렬 항성" 수준의 계층으로 충분
- 항성 클릭 시 세부 개념(마크다운 포스트)이 펼쳐지는 것으로 대체
- Phase 3 이후 재검토

### [A4] 유효 조회 기준
- **최소 30초 이상 체류 = 유효 조회**, `energy_value = 1.0`로 기록.
- **편집(Edit) / 업데이트 = 체류 시간 무관 항상 유효**, `energy_value = 2.0`.
- 모든 이벤트는 `view_events`에 `(duration_seconds, is_valid, is_edit, energy_value)`를 함께 기록한다.
- 생애주기 점수는 `is_valid = true`인 이벤트의 `energy_value` 합 (단순 카운트 아님).

### [A5] DB — PostgreSQL + pgvector
- MongoDB Atlas 벡터 검색 유료 → 채택 안 함
- **Railway PostgreSQL + pgvector** 사용
- FastAPI + SQLAlchemy(async) + asyncpg 조합
- UMAP, numpy가 모두 Python 생태계 → 임베딩 파이프라인 단일 언어로 구성 가능
- pgvector로 코사인 유사도 쿼리 처리

### [A6] Three.js — R3F(React Three Fiber) 채택
- Raw Three.js는 React 상태 동기화가 복잡
- **@react-three/fiber** + **@react-three/drei** 조합
- drei에서 글로우, 파티클, 카메라 컨트롤 모두 지원
- React 컴포넌트 단위로 항성/은하 관리 가능

---

## 3. 결정된 사항 (UI 렌더링)

### [A7] 은하 경계 — 반투명 성운(Nebula) 안개 효과
- 경계선 없는 클러스터(A)는 구분 불명확, 보로노이(C)는 딱딱한 느낌
- **반투명 성운 안개 Mesh로 은하 영역 표시** → R3F ShaderMaterial + alphaMap
- 각 은하마다 고유 색상의 성운 안개, 항성 클러스터를 부드럽게 감싸는 형태

### [A8] 은하 진입 트랜지션 — React Router 전환 + 진입 애니메이션
- URL 공유 가능성이 블로그 성격과 맞음 → B 채택
- `/universe` → `/galaxy/:id` → `/stars/:slug` URL 구조
- 페이지 전환 시 진입 애니메이션으로 성간 여행 느낌 구현

### [A9] 항성 레이블 — 줌 임계값 + hover 조합
- 줌 레벨 임계값 이상: 레이블 항상 표시 (drei `<Text>`)
- 줌 레벨 임계값 미만: hover 시에만 표시
- LOD와 자연스럽게 연동

### [A10] Nova 트리거 — 30초 자동 감지
- 30초 체류 완료 시 자동으로 Nova 애니메이션 + API 에너지 기록
- 프론트엔드 타이머로 30초 측정, 페이지 이탈 시 타이머 리셋

### [A11] 인트로 fly-in — 항성 클릭 시마다
- 은하 뷰에서 항성 클릭 → 해당 항성으로 카메라 fly-in
- MapControls의 target/position을 스프링 애니메이션으로 이동

### [A12] 모바일 — 웹 우선, 모바일 나중
- 현재 범위: 데스크탑 웹 브라우저만 지원
- 블로그 포스트 페이지(`/stars/:slug`)만 최소한의 모바일 반응형 고려

---

## 4. 결정된 사항 (아키텍처 핵심)

### [A13] 하이브리드 우주 모델 — 이중 공개 토글
- **기본은 개인 우주**: 각 유저는 본인만의 갤럭시/스타 소유
- **공개는 두 토글이 모두 true여야 노출**:
  - `User.is_universe_public` (기본 false): 유저 우주 마스터 스위치 (`PATCH /auth/me/settings`).
  - `Star.is_public` (기본 false): 항성 단위 공개 (`PATCH /stars/:id/visibility`).
- 공개 스타는 `/explore` 카드 피드와 `/:username/stars/:slug` URL에 노출.
- 비공개·미존재·유저 우주 비공개 모두 **403으로 통일** 반환 (404 분기 없음, enumeration 방어).

### [A14] URL 구조 — `/:username/stars/:slug` GitHub 방식
- 슬러그는 **유저 내 유일** (전역 유일 아님)
- 최종 URL 구조:
  ```
  /                          → RootRedirect (로그인 → /universe, 비로그인 → /universes)
  /universes                 → 비로그인 랜딩 + 공개 우주 카드 피드 (PublicUniversePage)
  /universe                  → 본인 개인 우주 (로그인 필요)
  /galaxy/:id                → 본인 은하 뷰 (로그인 필요)
  /galaxy/:id/new            → 항성 생성 풀페이지 (로그인 필요)
  /galaxy/:id/edit/:starId   → 항성 편집 풀페이지 (로그인 필요)
  /:username/stars/:slug     → 공개 스타 페이지 (비로그인 접근 가능)
  /explore                   → 공개 우주 카드 피드 (`updated_at desc` 정렬)
  /auth/login
  /auth/register
  ```

### [A15] 에너지 점수 — MVP 실시간 계산, 추후 배치 전환
- GET 요청 시마다 최근 30일 뷰 이벤트 집계해서 상태 반환
- 서비스 레이어(`lifecycle.py`)로 추상화 → 나중에 배치 job으로 교체 가능

### [A16] 좌표 배치 — UMAP 미사용, 휴리스틱 삽입
- 기존 항성 좌표는 **절대 변경하지 않는다** (사용자가 익힌 우주 지도 보존).
- 신규 항성 삽입 전략 (`umap_service.place_new_star`):
  1. 기존 항성 0개 → `(0, 0)`.
  2. 기존 항성 1개 → 단일 항성 기준 `(+12, 0)` + jitter.
  3. 기존 항성 2개 이상 → 코사인 유사도 상위 **k=3** 항성의 가중 중심점 계산.
  4. 모든 케이스에 ±6.0 단위 jitter를 더해 의미적으로 겹치는 항성도 클릭 가능하도록 분리.
- UMAP/차원축소는 도입하지 않는다. (의존성은 정리 예정.)
- 수동 재계산 엔드포인트는 현재 미제공. 도입 시 별도 명시적 라우트로만 노출.

### [A17] Nova 전파 — 코사인 유사도 상위 k=5 (고정)
- 웜홀 없이 코사인 유사도 단독으로 동작 (MVP).
- 유효 조회 또는 편집 이벤트 완료 시 → 같은 은하 내 상위 **5개** 항성에 `energy_value × 0.25` 전파 (`NOVA_ENERGY_RATIO = 0.25` 고정).
- 전파된 에너지는 대상 항성 `view_events`에 `energy_value = 0.25 또는 0.5`, `is_valid = true`로 별도 row로 적재.
- pgvector `<=>` 연산자로 동일 은하 내 상위 k 항성 쿼리.
- 1-hop 한정. 2-hop 전파는 구현 금지.

### [A18] 공개 토글 — 유저 레벨 + 항성 레벨 이중 구조
- `users.is_universe_public` (BOOLEAN, 기본 false): 유저 단위 마스터 스위치.
- `stars.is_public` (BOOLEAN, 기본 false): 항성 단위 토글.
- 공개 URL과 `/explore`는 **두 컬럼 모두 true**일 때만 데이터 반환.
- 토글 엔드포인트:
  - `PATCH /auth/me/settings` — 유저 레벨 (`is_universe_public`).
  - `PATCH /stars/:id/visibility` — 항성 레벨 (`is_public`).

---

## 5. 결정된 사항 (UX 세부)

### [A19] 검색 — Cmd+K 커맨드 팔레트 (MVP 포함)
- `Cmd+K` 단축키 → 커맨드 팔레트 오픈
- 항성 이름 검색 → 해당 항성으로 카메라 fly-in
- **항성 검색은 사이드바에 노출하지 않는다** (탐색 몰입감 보존). Cmd+K 단일 채널.
- `Sidebar` 컴포넌트는 존재하지만 검색이 아닌 보조 도구바(예: 은하 목록·생성·설정 진입점) 용도로만 쓴다.
- 라이브러리: `cmdk` (React 커맨드 팔레트 표준)

### [A20] 항성 생성/편집 — 풀페이지, 유사도 미리보기는 텍스트 리스트
- 항성 생성/편집은 **모달이 아닌 풀페이지**:
  - `/galaxy/:id/new` → `StarCreatePage`
  - `/galaxy/:id/edit/:starId` → `StarEditPage`
- 유사도 미리보기는 페이지 내 텍스트 리스트 ("이 개념들과 유사합니다: 버블정렬(92%), 선택정렬(87%)...").
  - 백엔드 엔드포인트: `POST /stars/preview-similar` (의도적으로 임베딩을 호출하는 GET 외 예외).
  - 유사도 0.5 초과 결과만 표시 (백엔드 필터링).
- 3D 미리보기는 Phase 2 이후 고려.

### [A21] 은하 색상 — 팔레트 자동 배정 + 변경 가능
- 생성 시 미리 정의된 색상 팔레트에서 자동 배정
- 생성 후 유저가 변경 가능
- `galaxies` 테이블 `color` 컬럼 (hex string)

### [A22] 한국어 슬러그 — 직접 입력 필드 (GitHub 방식)
- 제목 입력 시 영어 slug 자동 제안 (kebab-case 변환)
- 유저가 slug 필드 직접 수정 가능
- 제출 시 백엔드에서 유저 내 유일성 검증
- slug 자동 제안 로직: 프론트엔드에서 처리 (서버 부하 없음)

### [A23] `/explore` — MVP는 카드 피드, 3D 공유 우주는 장기 목표
- MVP: 공개된 항성들의 카드 그리드 (블로그 피드 형식).
- 정렬: `Star.updated_at desc` (최근 수정순). 페이지네이션은 `limit/offset` (기본 50, 최대 100).
- `/universes`는 비로그인 랜딩과 공개 피드를 함께 보여주는 별도 페이지 (히어로 섹션 + 카드 그리드).
- 유저별 임베딩 좌표계가 달라 단순 통합 시 무의미한 배치 → 3D 공유 우주는 장기 목표.

---

## 6. 구현 진행 상태

- [x] PostgreSQL 스키마 설계 (users, galaxies, stars, view_events, wormholes) — Alembic 마이그레이션 적용 완료
- [x] API 엔드포인트 1차 구현 — auth, galaxies, stars, explore 라우터
- [x] CLAUDE.md / PROJECT_DOCS.md / SKILLSET 문서 — 코드 현재 상태에 맞춰 1차 정합화
- [ ] 프론트엔드 단위 테스트 도입 (Vitest 등)
- [ ] Refresh token rotation
- [ ] 수동 좌표 재계산 엔드포인트 (필요 시)
- [ ] 웜홀 (Phase 2)
