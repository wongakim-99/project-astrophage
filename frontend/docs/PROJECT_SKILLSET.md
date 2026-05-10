# Frontend — 기술스택 명세

> React + React Three Fiber 기반. 우주 탐색 뷰(Three.js 씬)와 블로그 UI를 하나의 React 앱에서 구성한다.

---

## 핵심 스택

| 역할 | 기술 | 선택 이유 |
|------|------|----------|
| UI 프레임워크 | **React 18.3** | 컴포넌트 기반, R3F v8이 React 18 대상 |
| 빌드 도구 | **Vite 6** | 빠른 HMR, ESM 네이티브 |
| 언어 | **TypeScript** | Three.js 타입 지원, 대형 씬 관리에 필수 |
| 3D 렌더링 | **@react-three/fiber (R3F)** | Three.js를 React 컴포넌트로 선언적 관리 |
| 3D 헬퍼 | **@react-three/drei** | 카메라 컨트롤, 글로우, 텍스트, 파티클 등 |
| 후처리 효과 | **@react-three/postprocessing** | 블룸(Bloom), 글로우 효과 |
| 상태 관리 | **Zustand** | Three.js 렌더 루프와 궁합 좋음, 보일러플레이트 없음 |
| 라우팅 | **React Router v7** | URL 기반 씬 전환 (`/galaxy/:id`, `/:username/stars/:slug`) |
| 스타일링 | **TailwindCSS v4** | 블로그 UI, 오버레이 패널 스타일링 |
| 마크다운 렌더링 | **react-markdown** + **remark-gfm** | 공개 항성 페이지의 본문 렌더링 |
| 에디터 | **@tiptap/react** + **@tiptap/starter-kit** + **@tiptap/extension-placeholder** | 항성 본문 작성 (WYSIWYG + 마크다운 단축키) |
| 커맨드 팔레트 | **cmdk** | Cmd+K 항성 검색 → fly-in |
| HTTP 클라이언트 | **TanStack Query v5** + **axios** | API 캐싱, 로딩 상태 관리 |
| 폼 관리 | **React Hook Form** + **zod** + **@hookform/resolvers** | 항성/은하 폼 검증 |
| 애니메이션 | **@react-spring/three** | R3F 내 스프링 기반 트랜지션 |
| 아이콘 | **lucide-react** | 일관된 아이콘 셋 |

---

## 렌더링 씬 구조

### URL 라우팅 구조

```
/                          → RootRedirect (로그인 → /universe, 비로그인 → /universes)
/auth/login                → 로그인
/auth/register             → 회원가입
/universes                 → 비로그인 랜딩 + 공개 우주 카드 피드 (PublicUniversePage)
/universe                  → 본인 개인 우주 (로그인 필요)
/galaxy/:id                → 본인 은하 뷰 (로그인 필요)
/galaxy/:id/new            → 항성 생성 풀페이지 (로그인 필요)
/galaxy/:id/edit/:starId   → 항성 편집 풀페이지 (로그인 필요)
/:username/stars/:slug     → 공개 스타 페이지 (비로그인 접근 가능)
/explore                   → 공개 우주 카드 피드 (`updated_at desc`)
```

### 줌 레벨 3단계

```
[은하단 뷰]  /universe
  ├── 성운 안개로 감싸진 은하 클러스터들 표시
  ├── 항성 미표시
  └── 은하 클릭 → React Router → [은하 뷰] + 진입 애니메이션

[은하 뷰]   /galaxy/:id
  ├── 해당 은하의 항성 전체 표시 (백엔드 휴리스틱 좌표 × COORD_SCALE=4, z=0 고정)
  ├── 웜홀 연결선은 Phase 2 — 현재 미구현
  ├── 항성 이름 레이블 (줌 임계값 이상: 항상 표시 / 미만: hover만)
  └── 항성 클릭 → 카메라 fly-in + 우측 StarPanel 오픈

[항성 패널] /galaxy/:id + 우측 StarPanel
  ├── 클릭한 항성 중심으로 카메라 스프링 이동
  ├── 항성 메타데이터 + 본문(렌더 모드)
  ├── 삭제 버튼 + 인패널 확인 오버레이
  └── "편집" 클릭 시 풀페이지 /galaxy/:id/edit/:starId로 이동

[생성/편집] /galaxy/:id/new, /galaxy/:id/edit/:starId
  ├── 풀페이지 폼 (모달 아님)
  ├── Tiptap 에디터로 본문 작성
  └── 생성 페이지에서는 POST /stars/preview-similar 호출로 유사 항성 미리보기
```

### 카메라 컨트롤
- **MapControls** (drei) — 2D 탑뷰 팬/줌 (Google Maps 방식)
- 터치 지원: 핀치 줌, 단일 터치 팬

---

## 항성 시각 표현

### 생애주기별 색상/크기

| 상태 | 색상 | 크기 | 글로우 |
|------|------|------|--------|
| 주계열성 (Active) | `#A8D8FF` 청백색 | 1.4x | 강함 |
| 황색 왜성 (Normal) | `#FFD580` 노란색 | 1.0x | 중간 |
| 적색 거성 (Fading) | `#FF6B35` 붉은색 | 1.6x (팽창) | 약하고 흐릿 |
| 백색 왜성 (Forgotten) | `#E8E8E8` 흰색 | 0.6x | 거의 없음 |
| 암흑 물질 (Lost) | `#1A1A2E` 거의 검정 | 0.3x | 없음 |

### Nova 애니메이션
- 유효 조회 30초 완료 시 → API 호출 후 연결 항성들 0.5초 반짝임
- `@react-spring/three`로 opacity, scale 스프링 애니메이션

---

## 인증 플로우

```
Access Token → 메모리(Zustand authStore)에 저장
  - axios 인터셉터로 모든 요청에 자동 첨부
  - 401 응답 시 → /auth/refresh 자동 호출 → Access Token 갱신

Refresh Token → httpOnly 쿠키 (프론트엔드에서 직접 접근 불가)
  - 서버에서 Set-Cookie로 발급 (samesite=lax, 운영은 secure=true)
  - MVP는 rotation 없이 같은 refresh token을 만료까지 재사용

로그인 상태 유지:
  - 앱 마운트 시 authStore.init() → /auth/refresh 호출로 access token 복구
  - Refresh Token 만료 시 → 로그인 페이지로 리다이렉트
```

---

## 디렉토리 구조 (현재)

```
frontend/
├── src/
│   ├── main.tsx
│   ├── App.tsx              # 라우팅 루트, RootRedirect, 글로벌 Navbar/Sidebar/CmdKMenu
│   ├── pages/
│   │   ├── PublicUniversePage.tsx  # /universes — 비로그인 랜딩 + 공개 카드 피드
│   │   ├── UniversePage.tsx        # /universe — 본인 은하단 뷰
│   │   ├── GalaxyPage.tsx          # /galaxy/:id — 은하 뷰 + StarPanel
│   │   ├── StarCreatePage.tsx      # /galaxy/:id/new — 항성 생성 풀페이지
│   │   ├── StarEditPage.tsx        # /galaxy/:id/edit/:starId — 항성 편집 풀페이지
│   │   ├── StarPage.tsx            # /:username/stars/:slug — 공개 상세
│   │   ├── ExplorePage.tsx         # /explore — 카드 피드
│   │   ├── LoginPage.tsx
│   │   └── RegisterPage.tsx
│   ├── components/
│   │   ├── three/                  # R3F 3D 컴포넌트
│   │   │   ├── StarMesh.tsx
│   │   │   ├── GalaxyCluster.tsx
│   │   │   ├── BoundedMapControls.tsx
│   │   │   └── starShaders.ts
│   │   └── ui/                     # Tailwind 일반 UI
│   │       ├── Navbar.tsx
│   │       ├── Sidebar.tsx         # 검색 아닌 보조 도구바
│   │       ├── CmdKMenu.tsx        # cmdk 항성 검색
│   │       ├── StarPanel.tsx       # 항성 상세 패널 + 삭제 오버레이
│   │       ├── TiptapEditor.tsx    # 항성 본문 에디터
│   │       ├── StarCreateModal.tsx
│   │       └── GalaxyCreateModal.tsx
│   ├── stores/                     # Zustand 스토어
│   │   ├── authStore.ts
│   │   ├── galaxyStore.ts
│   │   ├── starStore.ts
│   │   └── uiStore.ts
│   ├── hooks/                      # TanStack Query 훅
│   │   ├── useGalaxies.ts
│   │   └── useStars.ts             # usePublicStars 포함
│   ├── lib/
│   │   ├── axios.ts                # axios 인스턴스 + 401 리프레시 인터셉터
│   │   └── queryClient.ts
│   ├── types/
│   │   └── api.ts                  # 응답 타입 + LIFECYCLE_STYLE 매핑
│   └── index.css
├── index.html
├── vite.config.ts
└── tsconfig.json
```

> 좌표 표시 시 화면에서는 `COORD_SCALE = 4`를 곱해 사용 (백엔드 좌표가 ±수십 단위 범위라 시각적으로 너무 가까이 모이는 것을 방지). 정의 위치: [`GalaxyPage.tsx`](src/pages/GalaxyPage.tsx).

---

## 30초 체류 타이머 플로우

```
항성 상세 패널 열림
  → 프론트엔드 타이머 시작 (30초)
  → 30초 완료 & 패널 닫히지 않음
    → POST /stars/:id/view { duration_seconds: 30, is_edit: false } 호출
    → 백엔드: view_events에 is_valid=true, energy_value=1.0 기록
       + 같은 은하 유사도 상위 5개 항성에 energy_value=0.25로 Nova 전파
    → 프론트엔드: Nova 애니메이션 트리거 (연결 항성 0.5초 반짝임)
  → 패널 닫히면 타이머 리셋 (30초 미달 시 조회 미기록)

편집 저장 시
  → POST /stars/:id/view { duration_seconds: 0, is_edit: true } (체류 무관 유효)
  → 백엔드: energy_value=2.0 기록 + Nova 전파 0.5
```

## 스코프 외 (명시적 제외)

- 모바일 우주 탐색 뷰 (데스크탑 전용)
- 블로그 포스트 페이지(`/:username/stars/:slug`)는 최소한의 반응형만
- 행성(Planet) 계층 구조 (Phase 3+)
- 프론트엔드 단위 테스트 (Vitest 등) — 도입 미정. 검증은 `tsc --noEmit` + `eslint` + `vite build` + 수동 브라우저 확인
